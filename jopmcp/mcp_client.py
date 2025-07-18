import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

transport = StreamableHttpTransport(url="http://localhost:8080/mcp")
client = Client(transport=transport)


def print_result(result) -> None:
    print("-" * 40)
    for e in result.content:
        if e.type == "text":
            print(e.text)
        elif e.type == "image":
            print(f"Image URL: {e.image_url}")
        elif e.type == "code":
            print(f"Code: {e.code}")
        else:
            print("Unknown content type:", e.type)
    print("-" * 40)


async def list_tools() -> None:
    async with client:
        result = await client.list_tools()
        for res in result:
            print("Tool:", res.name)
            print("Description:", res.description)
            print("-" * 40)

async def ping() -> None:
    async with client:
        result = await client.call_tool("ping")
        print_result(result)

async def list_notebook() -> None:
    async with client:
        result = await client.call_tool("list_notebooks")
        print_result(result)


async def find_notes_in_notebook() -> None:
    async with client:
        result = await client.call_tool(
            "find_notes_in_notebook", {"notebook_name": "3D printing"}
        )
        print_result(result)


async def get_note_by_id() -> None:
    async with client:
        result = await client.call_tool(
            "get_note_by_id", {"note_id": "7578b9d831e54d8698bc219da68fec99"}
        )
        print_result(result)


async def list_notes() -> None:
    async with client:
        result = await client.call_tool("list_notes")
        print_result(result)


async def find_notes() -> None:
    async with client:
        result = await client.call_tool("find_notes", {"query": "*french*london"})
        print_result(result)


async def create_note() -> None:
    async with client:
        result = await client.call_tool(
            "create_note",
            {
                "notebook_id": "e524bcad76ce4403bbf206fc39aecbdd",
                "title": "test note",
                "content": "This is a test note.",
            },
        )
        print_result(result)


async def create_note_todo() -> None:
    async with client:
        result = await client.call_tool(
            "create_note",
            {
                "notebook_id": "e524bcad76ce4403bbf206fc39aecbdd",
                "title": "test note",
                "content": "This is a test note.",
                "is_todo": True,
            },
        )
        print_result(result)


async def update_note() -> None:
    async with client:
        result = await client.call_tool(
            "update_note",
            {
                "note_id": "661706b8cb5b4cae89226a7ff6575064",
                "title": "Updated Note Title",
                "content": "This is the updated content of the note.",
            },
        )
        print_result(result)


async def create_notebook() -> None:
    async with client:
        result = await client.call_tool(
            "create_notebook",
            {
                "title": "Test Notebook",
            },
        )
        print_result(result)


async def update_notebook() -> None:
    async with client:
        result = await client.call_tool(
            "update_notebook",
            {
                "notebook_id": "c81009ccefd7409794e48574bf1d2230",
                "title": "Updated Notebook Title",
            },
        )
        print_result(result)


async def main() -> None:
    # await list_tools()
    await ping()
    # await list_notebook()
    # await find_notes_in_notebook()
    # await get_note_by_id()
    # await list_notes()
    # await find_notes()
    # await create_note()
    # await create_note_todo()
    # await update_note()
    # await create_notebook()
    # await update_notebook()


if __name__ == "__main__":
    asyncio.run(main())
