#! /usr/bin/env python3
# vim:fenc=utf-8

import atexit
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from tempfile import NamedTemporaryFile
import threading
from IPython.display import display, IFrame


SERVER: threading.Thread
TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <script type="module">
      import init, { COMPONENT } from "./PACKAGE";
      async function main() {
        await init();
        COMPONENT(document.getElementById("dioxus-component"));
      }
      main();
    </script>
  </head>
  <body>
    <div id="dioxus-component">DATA</div>
  </body>
</html>
"""
OPEN_WIDGETS = []
DIRECTORY = Path(".")


def init(package_path: str, port=8000, verbose=False):
    """Load the custom elements by executing the javascript."""
    global TEMPLATE, SERVER, DIRECTORY

    path = Path(package_path)
    TEMPLATE = TEMPLATE.replace("PACKAGE", path.name)
    DIRECTORY = path.parent
    SERVER = threading.Thread(
        target=serve,
        name="http server",
        args=[DIRECTORY, port, verbose]
    )
    SERVER.start()
    return SERVER, TEMPLATE


def show(
    component: str,
    data: str,
    width=500,
    height=500,
):
    """Present the data through a dioxus component"""
    global OPEN_WIDGETS

    w = NamedTemporaryFile(mode='w', dir=DIRECTORY, suffix=".html")
    w.write(
        TEMPLATE
        .replace("COMPONENT", component)
        .replace("DATA", data)
    )
    w.flush()
    OPEN_WIDGETS.append(w)

    url = "http://localhost:8000/" + Path(w.name).name
    display(IFrame(url, width, height))


def close():
    """Delete all temporary html files containing the widgets."""
    global OPEN_WIDGETS
    for w in OPEN_WIDGETS:
        w.close()
    OPEN_WIDGETS = []


def serve(directory, port, verbose):
    server_address = ('', port)

    if verbose:
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

        httpd = HTTPServer(server_address, Handler)

    else:
        class SilentHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

            def log_message(self, *_):
                return

        httpd = HTTPServer(server_address, SilentHandler)

    httpd.serve_forever()


atexit.register(close)
