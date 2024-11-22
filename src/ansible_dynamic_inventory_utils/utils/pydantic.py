import typing as t

from pydantic import BaseModel
from pydantic import ConfigDict


def instantiate_config_dict() -> ConfigDict:
    return ConfigDict(
        frozen=True,
        strict=True,
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
    )


class JsonModel(BaseModel):
    model_config = instantiate_config_dict() | ConfigDict(strict=True, extra="allow")


class FileModel(BaseModel):
    model_config = instantiate_config_dict()
    filename: str
    content: str


def extract_raw_fields(model: BaseModel, exclude: set[str] | None = None) -> dict[str, t.Any]:
    """model fields or extra fields を取得しそのままの値を格納した dict を返す"""
    return {k: getattr(model, k) for k in (model.model_fields.keys() | (model.model_extra or {}).keys()) if exclude is None or k not in exclude}
