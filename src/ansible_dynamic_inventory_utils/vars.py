from pydantic import BaseModel
from pydantic import ConfigDict

from ansible_dynamic_inventory_utils.utils.pydantic import extract_raw_fields
from ansible_dynamic_inventory_utils.utils.pydantic import instantiate_config_dict


class VarsBaseModel(BaseModel):
    """
    `extra = "allow"`
        TypeHint に記載した ConfigDict 情報を元にして再帰的な serialize/deserialize が行われる
        そのため TypeHint としての用途がメインの本クラスでは `extra = "allow"` を指定する必要がある
        本クラスを継承したクラスで `extra` を上書きすることは可能
    """

    model_config = instantiate_config_dict() | ConfigDict(extra="allow")

    def __add__(self, other: "VarsBaseModel") -> "AnyVars":
        """Merge two models. Prohibit duplicate keys."""
        my_dict = extract_raw_fields(self)
        other_dict = extract_raw_fields(other)
        if my_dict.keys() & other_dict.keys():
            err_msg = f"Duplicate keys: {my_dict.keys() & other_dict.keys()}"
            raise ValueError(err_msg)
        return AnyVars(**(my_dict | other_dict))

    def __iadd__(self, other: "VarsBaseModel") -> "AnyVars":
        """Merge two models. Prohibit duplicate keys."""
        return self.__add__(other)

    def __or__(self, other: "VarsBaseModel") -> "AnyVars":
        """Merge two models. Right precedence."""
        if isinstance(self, AnyVars) or isinstance(other, AnyVars):
            pass
        elif isinstance(other, self.__class__):
            err_msg = f"Cannot merge the same class: {self.__class__}"
            raise TypeError(err_msg)

        return AnyVars(**(extract_raw_fields(self) | extract_raw_fields(other)))

    def __ior__(self, other: "VarsBaseModel") -> "AnyVars":
        """Merge two models. Right precedence."""
        return self.__or__(other)


class AnyVars(VarsBaseModel):
    """VarsBaseModel に任意の型を指定できることを明示するためのクラス"""

    pass
