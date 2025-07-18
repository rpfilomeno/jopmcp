import asyncio
import logging
from typing import Annotated

from custom_logging import init_logging
from fastmcp import FastMCP
from joppy.client_api import ClientApi
from pydantic import Field

from jopmcp import config
from jopmcp import formatting as fmt
from jopmcp.models import ItemType

# Common fields list for note operations
COMMON_NOTE_FIELDS = (
    "id,title,body,created_time,updated_time,parent_id,is_todo,todo_completed"
)


mcp = FastMCP("jopmcp")
client = ClientApi(token=config.JOPLIN_TOKEN, url=config.JOPLIN_WEB_CLIPPER_URL)


@mcp.tool(name="ping", description="Ping Joplin to check connectivity")
def ping() -> str:
    res = client.ping()

    if res.status_code == 200:
        return "successful ping"
    else:
        return "ping failed"


@mcp.tool(name="list_notebooks", description="List all notebooks in Joplin")
def list_notebooks() -> str:
    fields_list = "id,title,created_time,updated_time,parent_id"
    results = client.get_all_notebooks(fields=fields_list)

    return fmt.format_item_list(results, ItemType.notebook)


@mcp.tool(
    name="find_notes_in_notebook",
    description="Find notes in a specific notebook, optionally filtered by task type and completion status",
)
async def find_notes_in_notebook(
    notebook_name: Annotated[str, Field(description="Notebook name to search in")],
) -> str:
    # Build search query with notebook and filters
    search_parts = [f"notebook:{notebook_name}".replace(" ", "_")]
    search_query = " ".join(search_parts)
    results = client.search_all(query=search_query, fields=COMMON_NOTE_FIELDS)

    return fmt.format_item_list(results, ItemType.note)


@mcp.tool(
    name="list_notes",
    description="List all notes in Joplin",
)
async def list_notes() -> str:
    results = client.get_all_notes(fields=COMMON_NOTE_FIELDS)
    return fmt.format_item_list(results, ItemType.note)


@mcp.tool(
    name="get_note_by_id",
    description="Get the content of a note by its ID",
)
async def get_note_by_id(
    note_id: Annotated[str, Field(description="Note ID to retrieve")],
) -> str:
    note = client.get_note(note_id, fields=COMMON_NOTE_FIELDS)
    return fmt.format_note_details(note)


@mcp.tool(
    name="find_notes",
    description="Find notes in Joplin using a search query. Supports wildcards '*'",
)
async def find_notes(
    query: Annotated[
        str, Field(description="Search query for notes. Wildcards '*' are supported")
    ],
) -> str:
    search_parts = [query]
    search_query = " ".join(search_parts)
    results = client.search_all(query=search_query, fields=COMMON_NOTE_FIELDS)

    return fmt.format_item_list(results, ItemType.note)


@mcp.tool(
    name="create_note",
    description="Create a new note in a specified notebook",
)
async def create_note(
    notebook_id: Annotated[str, Field(description="Notebook name")],
    title: Annotated[str, Field(description="Note title")],
    content: Annotated[str, Field(description="Note content")] = "",
    is_todo: Annotated[
        bool, Field(description="Create as todo (default: False)")
    ] = False,
) -> str:
    note = client.add_note(
        title=title, body=content, parent_id=notebook_id, is_todo=1 if is_todo else 0
    )
    return fmt.format_creation_success(ItemType.note, title, str(note))


@mcp.tool(
    name="update_note",
    description="Update an existing note in Joplin",
)
async def update_note(
    note_id: Annotated[str, Field(description="Note ID to update")],
    title: Annotated[str | None, Field(description="New title (optional)")] = None,
    content: Annotated[str | None, Field(description="New content (optional)")] = None,
    is_todo: Annotated[
        bool | None, Field(description="Convert to/from todo (optional)")
    ] = None,
    todo_completed: Annotated[
        bool | None, Field(description="Mark todo completed (optional)")
    ] = None,
) -> str:

    update_data: dict[str, str | int] = {}
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["body"] = content
    if is_todo is not None:
        update_data["is_todo"] = 1 if is_todo else 0
    if todo_completed is not None:
        update_data["todo_completed"] = 1 if todo_completed else 0

    if not update_data:
        raise ValueError("At least one field must be provided for update")

    client.modify_note(note_id, **update_data)
    return fmt.format_update_success(ItemType.note, note_id)


async def main() -> None:
    # TODO: allow other transports
    await mcp.run_streamable_http_async(host="localhost", port=8080, log_level="debug")

    # TODO: middlewares:
    # - error handling -> with obfuscation of token
    # - logging


if __name__ == "__main__":
    init_logging(config.LOGGING_CONFIG)
    asyncio.run(main())
