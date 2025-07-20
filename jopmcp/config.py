import os

MCP_PORT = int(os.getenv("MCP_PORT", "8080"))

LOGGING_CONFIG = os.getenv("LOGGING_CONFIG", "logging.conf")

JOPLIN_TOKEN: str = os.getenv("JOPLIN_TOKEN")  # type: ignore

assert (
    JOPLIN_TOKEN is not None and JOPLIN_TOKEN != ""
), "JOPLIN_TOKEN environment variable must be set"

JOPLIN_WEB_CLIPPER_URL = os.getenv("JOPLIN_WEB_CLIPPER_URL", "http://localhost:41184")
