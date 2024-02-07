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
      import init, { run, change } from "./PACKAGE";
      window.change = change;
      async function main() {
        await init();
        run();
      }
      main();
    </script>
  </head>
  <body>
    <TAG>DATA</TAG>
  </body>
</html>
"""
OPEN_WIDGETS = []
DIRECTORY = Path(".")


def init(package_path: str):
    """Load the custom elements by executing the javascript."""
    global TEMPLATE, SERVER, DIRECTORY

    path = Path(package_path)
    TEMPLATE = TEMPLATE.replace("PACKAGE", path.name)
    DIRECTORY = path.parent
    SERVER = threading.Thread(
        target=serve,
        name="http server",
        args=[DIRECTORY]
    )
    SERVER.start()
    return SERVER


def show(ce: str, data: str):
    """Present the data through a custom element"""
    global OPEN_WIDGETS

    w = NamedTemporaryFile(mode='w', dir=DIRECTORY, suffix=".html")
    w.write(TEMPLATE.replace("TAG", ce).replace("DATA", data))
    w.flush()
    OPEN_WIDGETS.append(w)

    url = "http://localhost:8000/" + Path(w.name).name
    display(IFrame(url, 500, 500))


def close():
    """Delete all temporary html files containing the widgets."""
    global OPEN_WIDGETS
    for w in OPEN_WIDGETS:
        w.close()
    OPEN_WIDGETS = []


def serve(directory):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    server_address = ('', 8000)
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()


atexit.register(close)
