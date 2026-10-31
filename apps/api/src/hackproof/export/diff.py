import logging
from typing import Any

logger = logging.getLogger(__name__)


def compute_diff(
    old_items: list[dict[str, Any]] | None,
    new_items: list[dict[str, Any]],
    key_field: str,
    target_name: str,
) -> dict[str, int]:
    """Compute and print changes between an existing export and the new export."""
    if not old_items:
        print(f"[{target_name}] Initial export: {len(new_items)} items created.")
        return {"added": len(new_items), "removed": 0, "modified": 0}

    old_map = {item[key_field]: item for item in old_items if key_field in item}
    new_map = {item[key_field]: item for item in new_items if key_field in item}

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())

    added = new_keys - old_keys
    removed = old_keys - new_keys
    common = old_keys & new_keys

    modified = set()
    for k in common:
        if old_map[k] != new_map[k]:
            modified.add(k)

    msg = (
        f"[{target_name} diff] +{len(added)} added, -{len(removed)} removed, "
        f"~{len(modified)} modified (total: {len(new_items)})"
    )
    print(msg)

    if added:
        for k in sorted(added)[:3]:
            print(f"  + Added: {k}")
        if len(added) > 3:
            print(f"  ... and {len(added) - 3} more")

    if removed:
        for k in sorted(removed)[:3]:
            print(f"  - Removed: {k}")
        if len(removed) > 3:
            print(f"  ... and {len(removed) - 3} more")

    if modified:
        for k in sorted(modified)[:3]:
            print(f"  ~ Modified: {k}")
        if len(modified) > 3:
            print(f"  ... and {len(modified) - 3} more")

    return {"added": len(added), "removed": len(removed), "modified": len(modified)}
