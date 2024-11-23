from pydantic import BaseModel
from pydantic import ConfigDict

from ansible_dynamic_inventory_utils.utils.pydantic import extract_raw_fields


class _SomeModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    a: int
    b: str


def test_extract_raw_fields():
    some = _SomeModel.model_validate({"a": 1, "b": "b", "c": "c"})

    assert extract_raw_fields(some) == {"a": 1, "b": "b", "c": "c"}
