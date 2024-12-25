from ansible_dynamic_inventory_utils.inventory import Inventory
from ansible_dynamic_inventory_utils.inventory import InventoryGroupModel
from ansible_dynamic_inventory_utils.type import HostNameType
from ansible_dynamic_inventory_utils.vars import AnyVars


def test_inventory():
    primary_value = 1
    overridden_value = 2

    inventory = Inventory(
        all=InventoryGroupModel(
            vars=AnyVars.model_validate({"aaa": primary_value}),
            hosts={
                # FIXME: if vars is overridden, error should be raised.
                #        Suppress errors by setting some option.
                HostNameType("host1"): AnyVars.model_validate({"aaa": overridden_value}),
            },
        )
    )
    assert inventory.make_dynamic_inventory_list()["_meta"]["hostvars"]["host1"]["aaa"] == overridden_value
    # TODO:
    # assert inventory.make_dynamic_inventory_list()["all"].get("vars") is None  # '.all.vars' は空にしてすべてを '_meta' の中にいれるべき
