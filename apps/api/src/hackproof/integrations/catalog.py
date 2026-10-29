from functools import lru_cache

import yaml
from pydantic import BaseModel, Field

from hackproof.config import get_settings


class Partner(BaseModel):
    slug: str
    name: str
    category: str
    site: str
    packages: dict[str, list[str]] = Field(default_factory=dict)
    endpoints: list[str] = Field(default_factory=list)
    github_owners: list[str] = Field(default_factory=list)


class Catalog(BaseModel):
    partners: list[Partner]

    def partner(self, slug: str) -> Partner:
        return next(partner for partner in self.partners if partner.slug == slug)


@lru_cache
def get_catalog() -> Catalog:
    with get_settings().integrations_file.open() as file:
        return Catalog.model_validate(yaml.safe_load(file))
