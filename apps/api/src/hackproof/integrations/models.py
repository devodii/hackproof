from typing import Literal

from pydantic import BaseModel, ConfigDict

Method = Literal["package", "endpoint"]


class Detection(BaseModel):
    model_config = ConfigDict(frozen=True)

    slug: str
    method: Method
    evidence: str
    path: str
