# libs
import os
from uvicorn import Server as UV_Server, Config as UV_Config
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# imports
from routers.nav import nav

# from fast_socket import websocket_endpoint


# =============================================================================
server_config: UV_Config
# print(os.environ.get("SITE_ENV"))

if os.environ.get("SITE_ENV") == "PRODUCTION":
    server_config = UV_Config(
        app="main:app",
        host="0.0.0.0",
        port=8062,
        root_path=".",
        workers=5,
        log_level="info",
    )
else:
    server_config = UV_Config(
        app="main:app",
        host="0.0.0.0",
        port=8062,
        root_path=".",
        log_level="debug",
        workers=5,
        ssl_certfile="./certs/dev-cert.pem",
        ssl_keyfile="./certs/dev-key.pem",
    )

server: UV_Server = UV_Server(server_config)


app = FastAPI(root_path=".")
origins: list[str] = ["http://localhost", "http://127.0.0.1", "http://[::]", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------

app.mount(path="/public", app=StaticFiles(directory="public"), name="public")
app.mount(
    path="/senza",
    app=StaticFiles(directory="senza"),
    name="senza",
)
app.mount(
    path="/web",
    app=StaticFiles(directory="web"),
    name="web",
)
# ---------------------------------------------------------
app.include_router(nav)
# ---------------------------------------------------------


@app.get("/status")
def get_status() -> dict[str, str]:
    return {"status": "ok"}


# @app.get("/favicon.ico")
# def get_favicon() -> FileResponse:
#     return FileResponse(path="public/favicon.ico", status_code=200)


@app.get("/")
def get_home() -> HTMLResponse:
    html: str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <!-- ============================================================ -->
    <link defer rel="stylesheet" href="/public/index.css" />
    <link defer rel="stylesheet" href="https://pyscript.net/releases/2024.6.1/core.css">
    <script defer type="module" src="https://pyscript.net/releases/2024.6.1/core.js"></script>
    <!-- ============================================================ -->
    <title>Pyscript App</title>
  </head>
  <body>
    <!-- ============================================================ -->
   <script type='py' src='/web/app.py' config='/web/config.toml'></script>
        </body>
        </html>
    """
    return HTMLResponse(html, status_code=200)


# ------------------------------------------------------------------------------


@app.websocket("/ws")
async def websocket_text(websocket: WebSocket):
    await websocket.accept()
    while True:
        # data = await websocket.receive_text()
        # await websocket.send_text(data)
        #
        # data = await websocket.receive_json()
        # await websocket.send_json(data)
        #
        data = await websocket.receive_bytes()
        await websocket.send_bytes(data)


if __name__ == "__main__":
    server.run()
