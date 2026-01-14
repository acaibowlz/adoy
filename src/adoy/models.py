from pydantic import BaseModel


class SiteConfig(BaseModel):
    title: str
    subtitle: str
    description: str
    url: str
    base_path: str


class PathConfig(BaseModel):
    contents: str
    templates: str
    static: str
    output: str


class ContentConfig(BaseModel):
    section: str
    template: str
    permalink: str


class BuildConfig(BaseModel):
    paginate: int
    timezone: str


class TemplateConfig(BaseModel):
    default: str
    base: str


class TaxonomyConfig(BaseModel):
    field: str
    path: str
    applies_to: list[str]
    template_index: str
    template_key: str
