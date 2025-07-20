# Jopmcp

Jopmcp is a MCP server for [Joplin](https://joplinapp.org/), a note-taking and
to-do application with synchronization capabilities. My implementation of this
MCP is largely inspired by [this one](https://github.com/alondmnt/joplin-mcp),
but adapted to my needs. In particular:

- Docker is used to run the server (I run all my MCPs in Docker).
- It supports paths: `Notebook > Subnotebook > Note Title`, so the LLM
  understand the hierarchy of notes.

I felt the need to implement this MCP myself because Joplin is an essential tool
for me (storing very sensitive data) so I wanted to have full control over the
implementation of the MCP.


## Run in docker-compose

I normally run all my MCPs in Docker. I have a `docker-compose.yml` file
somewhere that spins up all my MCPs. To run this MCP, follow these steps:

1. Configure Joplin
    - Open Joplin Desktop → Tools → Options → Web Clipper
    - Enable the Web Clipper service
    - Copy the Authorization token

2. Set the environment variable `JOPLIN_TOKEN` with the token you copied
   from Joplin. You can do this in your shell or in a `.env` file.

3. Build the `jopmcp` image: `make pkg`

4. Run the MCP with `docker-compose up -d`

```yaml
services:
  joplin:
    image: jopmcp:latest
    container_name: jopmcp
    network_mode: "host"
    environment:
      - JOPLIN_TOKEN=${JOPLIN_TOKEN}
      - MCP_PORT=8002
```

The network mode needs to be set to `host` so that the MCP can access the Joplin
web clipper API, running on localhost:41184 by default. If you're running the
web clipper on a different port, you can set the `JOPLIN_WEB_CLIPPER_URL` env
var.

## Docs

- [Joplin data API](https://joplinapp.org/help/api/references/rest_api)
- [Joplin search](https://joplinapp.org/help/apps/search/)

