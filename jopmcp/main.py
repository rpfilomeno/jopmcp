import asyncio
import logging
from typing import Annotated

import joppy.data_types as dt
from custom_logging import init_logging
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from joppy.client_api import ClientApi
from pydantic import Field

from jopmcp import config
from jopmcp import formatting as fmt
from jopmcp.models import ItemType

logger = logging.getLogger(__name__)

# Common fields list for note operations
COMMON_NOTE_FIELDS = (
    "id,title,body,created_time,updated_time,parent_id,is_todo,todo_completed"
)


client = ClientApi(token=config.JOPLIN_TOKEN, url=config.JOPLIN_WEB_CLIPPER_URL)
mcp = FastMCP("jopmcp")

mcp.add_middleware(ErrorHandlingMiddleware(logger=logger, include_traceback=True))


def build_paths() -> dict[str, str]:

    notes = client.get_all_notes(fields=COMMON_NOTE_FIELDS)
    notebooks = client.get_all_notebooks(fields="id,title,parent_id")
    items = notes + notebooks

    nodes = {i.id: i for i in items}
    output: dict[str, str] = {}

    for it in items:
        if it.id is None:
            continue

        n: dt.NotebookData | dt.NoteData | None = it
        parents: list[str] = []

        while n is not None:
            title = getattr(n, "title", "Untitled")
            parents.append(title)
            n = nodes.get(n.parent_id, None)

        if parents:
            path = " > ".join(list(reversed(parents)))
            output[it.id] = path

    return output


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
    return fmt.format_item_list(results, ItemType.notebook, paths=build_paths())


@mcp.tool(
    name="find_notes_in_notebook",
    description="Find notes in a specific notebook, optionally filtered by task type and completion status",
)
async def find_notes_in_notebook(
    notebook_name: Annotated[str, Field(description="Notebook name to search in")],
) -> str:
    search_parts = [f"notebook:{notebook_name}".replace(" ", "_")]
    search_query = " ".join(search_parts)
    results = client.search_all(query=search_query, fields=COMMON_NOTE_FIELDS)
    return fmt.format_item_list(results, ItemType.note, paths=build_paths())


@mcp.tool(
    name="list_notes",
    description="List all notes in Joplin",
)
async def list_notes() -> str:
    notes = client.get_all_notes(fields=COMMON_NOTE_FIELDS)
    return fmt.format_item_list(notes, ItemType.note, paths=build_paths())


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

    return fmt.format_item_list(results, ItemType.note, paths=build_paths())


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


@mcp.tool(
    name="create_notebook",
    description="Create a new notebook (folder) in Joplin to organize your notes",
)
async def create_notebook(
    title: Annotated[str, Field(description="Notebook title")],
    parent_id: Annotated[
        str | None, Field(description="Parent notebook ID (optional)")
    ] = None,
) -> str:
    notebook_kwargs = {"title": title}
    if parent_id:
        notebook_kwargs["parent_id"] = parent_id.strip()

    notebook = client.add_notebook(**notebook_kwargs)
    return fmt.format_creation_success(ItemType.notebook, title, str(notebook))


@mcp.tool(
    name="update_notebook",
    description="Update an existing notebook in Joplin",
)
async def update_notebook(
    notebook_id: Annotated[str, Field(description="Notebook ID to update")],
    title: Annotated[str, Field(description="New notebook title")],
) -> str:
    client.modify_notebook(notebook_id, title=title)
    return fmt.format_update_success(ItemType.notebook, notebook_id)


async def main() -> None:
    # TODO: allow other transports
    # await mcp.run_streamable_http_async(host="localhost", port=8080, log_level="debug")
    await mcp.run_http_async(
        show_banner=False,
        transport="streamable-http",
        host="localhost",
        port=8080,
        log_level="debug",
        uvicorn_config={"log_config": config.LOGGING_CONFIG},
    )

    # TODO: middlewares:
    # - error handling -> with obfuscation of token
    # - logging


if __name__ == "__main__":
    init_logging(config.LOGGING_CONFIG)
    asyncio.run(main())
