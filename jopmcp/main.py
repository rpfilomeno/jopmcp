import asyncio
import logging
from typing import Annotated

import joppy.data_types as dt
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from joppy.client_api import ClientApi
from pydantic import Field

from custom_logging import init_logging
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
    """Builds a dictionary mapping item IDs to their hierarchical paths in Joplin.

    This function retrieves all notes and notebooks, constructs a path for each items
    based on their parent-child relationships, and returns a dictionary where keys are
    item IDs and values are their paths in the format 'Parent > Child > Item'.

    Returns:
        A dictionary mapping item IDs to their hierarchical paths.
        Example: {'note_id_1': 'Notebook > Subnotebook > Note Title', ...}

    """
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
    """Ping the Joplin server to check connectivity.

    Returns:
        str: A message indicating whether the ping was successful or failed.

    """
    res = client.ping()

    if res.status_code == 200:
        return "successful ping"
    else:
        return "ping failed"


@mcp.tool(name="list_notebooks", description="List all notebooks in Joplin")
def list_notebooks() -> str:
    """List all notebooks in Joplin.

    Returns:
        str: A formatted string listing all notebooks with their details.

    """
    fields_list = "id,title,created_time,updated_time,parent_id"
    results = client.get_all_notebooks(fields=fields_list)
    return fmt.format_item_list(results, ItemType.notebook, paths=build_paths())


@mcp.tool(
    name="find_notes_in_notebook",
    description="Find notes in a specific notebook",
)
async def find_notes_in_notebook(
    notebook_name: Annotated[str, Field(description="Notebook name to search in")],
) -> str:
    """Find notes in a specific notebook by its name.

    Args:
        notebook_name: The name of the notebook to search in.
    Returns:
        str: A formatted string listing all notes found in the specified notebook.

    """
    search_parts = [f"notebook:{notebook_name}".replace(" ", "_")]
    search_query = " ".join(search_parts)
    results = client.search_all(query=search_query, fields=COMMON_NOTE_FIELDS)
    return fmt.format_item_list(results, ItemType.note, paths=build_paths())


@mcp.tool(
    name="list_notes",
    description="List all notes in Joplin",
)
async def list_notes() -> str:
    """List all notes in Joplin.

    Returns:
        A formatted string listing all notes with their details.
    """
    notes = client.get_all_notes(fields=COMMON_NOTE_FIELDS)
    return fmt.format_item_list(notes, ItemType.note, paths=build_paths())


@mcp.tool(
    name="get_note_by_id",
    description="Get the content of a note by its ID",
)
async def get_note_by_id(
    note_id: Annotated[str, Field(description="Note ID to retrieve")],
) -> str:
    """Get the content of a note by its ID.

    Args:
        note_id: The ID of the note to retrieve.

    Returns:
        str: A formatted string with the note's details.

    """
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
    """Find notes in Joplin using a search query.

    Args:
        query: The search query to find notes. Supports wildcards '*'.

    Returns:
        A formatted string listing all notes that match the search query.

    """
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
    """Create a new note in a specified notebook.

    Args:
        notebook_id: The ID of the notebook where the note will be created.
        title: The title of the new note.
        content: The content of the new note (default is empty).
        is_todo: Whether to create the note as a todo (default is False).

    Returns:
        A formatted string indicating the success of the note creation.

    """
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
    """Update an existing note in Joplin.

    Args:
        note_id: The ID of the note to update.
        title: The new title for the note (optional).
        content: The new content for the note (optional).
        is_todo: Whether to convert the note to a todo (optional).
        todo_completed: Whether to mark the todo as completed (optional).

    Raises:
        ValueError: If no fields are provided for update.

    Returns:
        A formatted string indicating the success of the note update.

    """
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
    """Create a new notebook in Joplin.

    Args:
        title: The title of the new notebook.
        parent_id: The ID of the parent notebook (optional).

    Returns:
        A formatted string indicating the success of the notebook creation.

    """
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
    """Update an existing notebook in Joplin.

    Args:
        notebook_id: The ID of the notebook to update.
        title: The new title for the notebook.

    Returns:
        A formatted string indicating the success of the notebook update.

    """
    client.modify_notebook(notebook_id, title=title)
    return fmt.format_update_success(ItemType.notebook, notebook_id)


async def main() -> None:
    await mcp.run_http_async(
        show_banner=False,
        transport="streamable-http",
        host="localhost",
        port=config.MCP_PORT,
        log_level="debug",
        uvicorn_config={"log_config": config.LOGGING_CONFIG},
    )


if __name__ == "__main__":
    init_logging(config.LOGGING_CONFIG)
    asyncio.run(main())
