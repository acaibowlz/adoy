from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class SiteConfig(BaseModel):
    title: str
    subtitle: str
    description: str
    url: str
    base_path: str


class PathConfig(BaseModel):
    content: str = "content/"
    templates: str = "templates/"
    static: str = "static/"
    output: str = "public/"


class ContentConfig(BaseModel):
    section: str
    template: str
    permalink: str


class PageConfig(BaseModel):
    template: str
    permalink: str


class BuildConfig(BaseModel):
    paginate: int
    timezone: str


class TemplateConfig(BaseModel):
    default: str
    base: str


class TaxonomyConfig(BaseModel):
    name: str                   # taxonomy name, e.g. "tags", "series"
    path: str                   # URL path for the taxonomy overview page
    applies_to: list[str]       # section names this taxonomy applies to
    sort_by: str                # how to sort pages in the taxonomy overview page
    template_taxonomy: str      # template for the taxonomy overview page
    template_term: str          # template for individual taxonomy term pages


class Config(BaseModel):
    site: SiteConfig
    paths: PathConfig = PathConfig()
    build: BuildConfig
    template: TemplateConfig
    content: dict[str, ContentConfig] = {}
    pages: dict[str, PageConfig] = {}
    taxonomy: dict[str, TaxonomyConfig] = {}


class FrontMatter(BaseModel):
    model_config = {"extra": "allow"}

    title: str
    description: str
    summary: str
    date: datetime
    content_type: str
    slug: str
    status: str                 # active/draft/archive


class Page(BaseModel):
    front_matter: FrontMatter
    body: str                   # raw Markdown
    source_path: Path

    model_config = {"arbitrary_types_allowed": True}


class ContentCacheEntry(BaseModel):
    checksum: str
    output_path: str
    taxonomy_terms: dict[str, list[str]]  # e.g. {"tags": ["python"], "series": ["my-series"]}


class CacheStore(BaseModel):
    config_checksum: str
    template_checksums: dict[str, str]      # template path -> checksum
    content: dict[str, ContentCacheEntry]   # source path -> entry
