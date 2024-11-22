import json


def sort_json_string(json_string: str, *, indent: str | int | None = None) -> str:
    """Sorts a JSON string recursively by keys.

    Args:
      json_string: The JSON string to be sorted.

    Returns:
      The sorted JSON string.
    """
    return json.dumps(json.loads(json_string), indent=indent, sort_keys=True)
