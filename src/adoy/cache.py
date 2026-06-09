import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from adoy.models import CacheStore, Config, ContentCacheEntry

CACHE_FILE = ".adoy-cache.json"


@dataclass
class BuildPlan:
    full_rebuild: bool = False
    content_to_build: set[Path] = field(default_factory=set)   # new + modified content files
    content_to_delete: set[Path] = field(default_factory=set)  # deleted content files
    taxonomy_terms_to_rebuild: dict[str, set[str]] = field(default_factory=dict)  # taxonomy -> terms


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache(project_root: Path) -> CacheStore:
    cache_file = project_root / CACHE_FILE
    if not cache_file.exists():
        return CacheStore(config_checksum="", template_checksums={}, content={})
    with cache_file.open() as f:
        return CacheStore.model_validate(json.load(f))


def save_cache(cache: CacheStore, project_root: Path) -> None:
    cache_file = project_root / CACHE_FILE
    with cache_file.open("w") as f:
        json.dump(cache.model_dump(), f, indent=2)


def diff(cache: CacheStore, config: Config, project_root: Path) -> BuildPlan:
    plan = BuildPlan()

    # Check config
    config_checksum = checksum(project_root / "adoy.toml")
    if config_checksum != cache.config_checksum:
        plan.full_rebuild = True
        return plan

    # Check templates
    templates_dir = project_root / config.paths.templates
    changed_templates: set[str] = set()
    for template_path in templates_dir.rglob("*"):
        if not template_path.is_file():
            continue
        rel = str(template_path.relative_to(templates_dir))
        current = checksum(template_path)
        if cache.template_checksums.get(rel) != current:
            changed_templates.add(rel)

    # Check content files
    content_dir = project_root / config.paths.content
    current_files: set[str] = set()

    for content_path in content_dir.rglob("*.md"):
        rel = str(content_path.relative_to(project_root))
        current_files.add(rel)
        current = checksum(content_path)
        cached = cache.content.get(rel)

        if cached is None or cached.checksum != current:
            plan.content_to_build.add(content_path)
        elif changed_templates:
            # Rebuild if the content's template was changed
            section = content_path.relative_to(content_dir).parts[0]
            content_config = config.content.get(section)
            if content_config and content_config.template in changed_templates:
                plan.content_to_build.add(content_path)

    # Rebuild taxonomy pages whose templates changed
    for tax_name, tax_config in config.taxonomy.items():
        if tax_config.template_taxonomy in changed_templates or tax_config.template_term in changed_templates:
            plan.taxonomy_terms_to_rebuild.setdefault(tax_name, set())

    # Detect deleted content files
    for cached_rel in cache.content:
        if cached_rel not in current_files:
            plan.content_to_delete.add(project_root / cached_rel)

    # Collect affected taxonomy terms for modified/deleted content
    affected = plan.content_to_build | plan.content_to_delete
    for content_path in affected:
        rel = str(content_path.relative_to(project_root))
        cached = cache.content.get(rel)
        if cached:
            for taxonomy, terms in cached.taxonomy_terms.items():
                plan.taxonomy_terms_to_rebuild.setdefault(taxonomy, set()).update(terms)

    return plan


def update_cache(
    cache: CacheStore,
    config: Config,
    project_root: Path,
    built: dict[Path, ContentCacheEntry],
    deleted: set[Path],
) -> CacheStore:
    """Return an updated CacheStore after a build."""
    # Recompute config and template checksums
    config_checksum = checksum(project_root / "adoy.toml")
    templates_dir = project_root / config.paths.templates
    template_checksums = {
        str(p.relative_to(templates_dir)): checksum(p)
        for p in templates_dir.rglob("*")
        if p.is_file()
    }

    # Merge content entries
    content = dict(cache.content)
    for path, entry in built.items():
        rel = str(path.relative_to(project_root))
        content[rel] = entry
    for path in deleted:
        rel = str(path.relative_to(project_root))
        content.pop(rel, None)

    return CacheStore(
        config_checksum=config_checksum,
        template_checksums=template_checksums,
        content=content,
    )
