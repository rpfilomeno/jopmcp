import datetime

import joppy.data_types as dt

from jopmcp.models import ItemType


def format_item_list(items: list, item_type: ItemType, paths: dict[str, str]) -> str:
    """Format a list of items (notebooks, tags, etc.) for display optimized for LLM comprehension."""
    if not items:
        return f"ITEM_TYPE: {item_type.value}\nTOTAL_ITEMS: 0\nSTATUS: No {item_type.value}s found in Joplin instance"

    count = len(items)
    result_parts = [f"ITEM_TYPE: {item_type.value}", f"TOTAL_ITEMS: {count}", ""]

    for i, item in enumerate(items, 1):
        title = getattr(item, "title", "Untitled")
        item_id = getattr(item, "id", "unknown")

        # Structured item entry
        result_parts.extend(
            [
                f"ITEM_{i}:",
                f"  {item_type.value}_id: {item_id}",
                f"  title: {title}",
            ]
        )

        if item_id in paths:
            result_parts.append(f"  path: {paths[item_id]}")

        # Add parent folder ID if available (for notebooks)
        parent_id = getattr(item, "parent_id", None)
        if parent_id:
            result_parts.append(f"  parent_id: {parent_id}")

        # Add creation time if available
        created_time = getattr(item, "created_time", None)
        if created_time and isinstance(created_time, datetime.datetime):
            result_parts.append(f"  created: {created_time.isoformat()}")

        # Add update time if available
        updated_time = getattr(item, "updated_time", None)
        if updated_time and isinstance(updated_time, datetime.datetime):
            result_parts.append(f"  updated: {updated_time.isoformat()}")

        result_parts.append("")

    return "\n".join(result_parts)


def format_note_details(note: dt.NoteData) -> str:
    """Format a note for detailed display optimized for LLM comprehension."""
    title = getattr(note, "title", "Untitled")
    note_id = getattr(note, "id", "unknown")

    # Structured note details - metadata first
    result_parts = [
        f"note_id: {note_id}",
        f"title: {title}",
    ]

    # Add structured metadata first
    created_time = getattr(note, "created_time", None)
    if created_time and isinstance(created_time, datetime.datetime):
        result_parts.append(f"created: {created_time.isoformat()}")

    updated_time = getattr(note, "updated_time", None)
    if updated_time and isinstance(updated_time, datetime.datetime):
        result_parts.append(f"updated: {updated_time.isoformat()}")

    # Notebook reference
    parent_id = getattr(note, "parent_id", None)
    if parent_id:
        result_parts.append(f"notebook_id: {parent_id}")

    is_todo = getattr(note, "is_todo", 0)
    if is_todo:
        result_parts.append("is_todo: true")
        todo_completed = getattr(note, "todo_completed", 0)
        result_parts.append(f"todo_completed: {'true' if todo_completed else 'false'}")
    else:
        result_parts.append("is_todo: false")

    body = getattr(note, "body", "")
    if body:
        result_parts.append(f"content: {body}")

    return "\n".join(result_parts)


def format_creation_success(item_type: ItemType, title: str, item_id: str) -> str:
    return f"""operation: create_{item_type.value}
        status: success
        item_type: {item_type.value}
        item_id: {item_id}
        title: {title}
        message: {item_type.value} created successfully in Joplin
        """.replace(
        "        ", ""
    ).strip()


def format_update_success(item_type: ItemType, item_id: str) -> str:
    return f"""operation: update_{item_type.value}
        status: success
        item_type: {item_type.value}
        item_id: {item_id}
        message: {item_type.value} updated successfully in Joplin
        """.replace(
        "        ", ""
    ).strip()
