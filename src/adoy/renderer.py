from pathlib import Path

import mistune
from jinja2 import Environment, FileSystemLoader

from adoy.models import Config, FrontMatter, Page


class Renderer:
    def __init__(self, config: Config, project_root: Path) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(project_root / config.paths.templates)),
            autoescape=False,
        )
        self._env.globals["site"] = config.site
        self._md = mistune.create_markdown()

    def render(self, page: Page, template_name: str, extra: dict | None = None) -> str:
        template = self._env.get_template(template_name)
        return template.render(
            page=page.front_matter,
            content=self._md(page.body),
            **(extra or {}),
        )

    def render_taxonomy_overview(
        self,
        taxonomy_name: str,
        terms: dict[str, list[FrontMatter]],
        template_name: str,
    ) -> str:
        template = self._env.get_template(template_name)
        return template.render(taxonomy=taxonomy_name, terms=terms)

    def render_taxonomy_term(
        self,
        taxonomy_name: str,
        term: str,
        pages: list[FrontMatter],
        template_name: str,
    ) -> str:
        template = self._env.get_template(template_name)
        return template.render(taxonomy=taxonomy_name, term=term, pages=pages)
