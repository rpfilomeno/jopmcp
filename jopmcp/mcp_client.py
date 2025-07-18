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


async def get_note() -> None:
    async with client:
        result = await client.call_tool(
            "get_note", {"note_id": "7578b9d831e54d8698bc219da68fec99"}
        )
        print_result(result)


async def main() -> None:
    # await list_tools()
    # await list_notebook()
    await find_notes_in_notebook()
    # await get_note()


if __name__ == "__main__":
    asyncio.run(main())
