import typing as t

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer

from ansible_dynamic_inventory_utils.type import HostNameType
from ansible_dynamic_inventory_utils.utils.pydantic import instantiate_config_dict
from ansible_dynamic_inventory_utils.vars import AnyVars
from ansible_dynamic_inventory_utils.vars import VarsBaseModel


class InventoryGroupModel(BaseModel):
    """an example as below:
    ```
    vars: {}
    hosts:
      example.com:
        vars:
          fizz: FIZZ
          buzz: BUZZ
    children:
      subgroup
    ```
    """

    model_config = instantiate_config_dict()
    vars: VarsBaseModel = AnyVars()
    # hosts: dict[HostNameType, dict[str, t.Any] | BaseModel] = Field(default_factory=dict)
    hosts: dict[HostNameType, VarsBaseModel] = Field(default_factory=dict)
    children: dict[str, "InventoryGroupModel"] = Field(default_factory=dict)


class Inventory(BaseModel):
    model_config = instantiate_config_dict()
    all: InventoryGroupModel = Field(default_factory=InventoryGroupModel)

    def make_dynamic_inventory_list(self) -> dict[str, t.Any]:
        return make_dynamic_inventory_list(self)

    def get_names_of_hosts(self) -> list[HostNameType]:
        def _get_names_of_hosts(group: InventoryGroupModel) -> set[HostNameType]:
            ret = set(group.hosts.keys())
            for child in group.children.values():
                ret |= _get_names_of_hosts(child)
            return ret

        return sorted(_get_names_of_hosts(self.all))


class GroupModel(BaseModel):
    model_config = instantiate_config_dict()
    vars: VarsBaseModel | None = None
    hosts: list[HostNameType] = Field(default_factory=list)
    children: list[str] = Field(default_factory=list)

    @field_serializer("hosts", "children")
    def serialize_in_order(self, value: list[HostNameType] | list[str]) -> list[HostNameType] | list[str]:
        return sorted(value)

    def __or__(self, other: t.Self) -> t.Self:
        return self.__class__(
            # 同一 key があった場合は other が上書き
            vars=AnyVars.model_validate(
                (self.vars.model_dump() if self.vars is not None else {}) | (other.vars.model_dump() if other.vars is not None else {})
            ),
            hosts=list(set(self.hosts + other.hosts)),
            children=list(set(self.children + other.children)),
        )

    def __ior__(self, other: t.Self) -> t.Self:
        return self.__or__(other)


class Meta(BaseModel):
    model_config = instantiate_config_dict()
    hostvars: dict[HostNameType, t.Any] = Field(default_factory=dict)


def make_dynamic_inventory_list(inventory: Inventory) -> dict[str, t.Any]:
    def insert_group_(ret_groups: dict[str, t.Any], ret_hostvars: dict[HostNameType, VarsBaseModel], group_name: str, group: InventoryGroupModel) -> None:
        for h_name, h_vars in group.hosts.items():
            # FIXME:
            ret_hostvars[h_name] |= h_vars

        for g_name, g in group.children.items():
            insert_group_(ret_groups=ret_groups, ret_hostvars=ret_hostvars, group_name=g_name, group=g)

        if group_name not in ret_groups:
            ret_groups[group_name] = GroupModel()
        ret_groups[group_name] |= GroupModel(
            vars=group.vars,
            hosts=list(group.hosts.keys()),
            children=list(group.children.keys()),
        )

    _ret: dict[str, GroupModel | Meta] = {
        "all": GroupModel(
            vars=inventory.all.vars,
            hosts=list(inventory.all.hosts.keys()),
            children=list(inventory.all.children.keys()),
        )
    }

    hostvars: dict[HostNameType, VarsBaseModel] = inventory.all.hosts
    for group_name, group in inventory.all.children.items():
        insert_group_(_ret, hostvars, group_name, group)
    _ret["_meta"] = Meta(hostvars=hostvars)
    return {name: model.model_dump(exclude_none=True) for name, model in _ret.items()}
