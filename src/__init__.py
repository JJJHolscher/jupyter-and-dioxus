#! /usr/bin/env python3
# vim:fenc=utf-8

import atexit
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from tempfile import NamedTemporaryFile
import threading
import time

from IPython.display import display, IFrame, clear_output

import ipywidgets as widgets
from jupyter_ui_poll import ui_events


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
    # Do cleanup of past `open` calls that weren't closed.
    for f in DIRECTORY.iterdir():
        if f.name[:27] == "__tmp_dioxus_widget_iframe_":
            f.unlink()

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
    no_display=False,
):
    """Present the data through a dioxus component"""
    global OPEN_WIDGETS

    w = NamedTemporaryFile(
        mode='w',
        dir=DIRECTORY,
        prefix="__tmp_dioxus_widget_iframe_",
        suffix=".html"
    )
    w.write(
        TEMPLATE
        .replace("COMPONENT", component)
        .replace("DATA", data)
    )
    w.flush()
    OPEN_WIDGETS.append(w)

    url = "http://localhost:8000/" + Path(w.name).name
    iframe = IFrame(url, width, height)
    if no_display:
        return iframe
    else:
        display(iframe)


def debug(
    component: str,
    data: str,
    width=500,
    height=500,
):
    """Call the `show` function whenever the dioxus package files change.
    This function keeps the cell running until the `Stop` button is pressed.
    """
    global OPEN_WIDGETS

    # A button for stopping to watch for file changes.
    stop = False
    button = widgets.Button(description="Stop")

    def stop_widget(_):
        nonlocal stop
        stop = True
    button.on_click(stop_widget)

    def render():
        iframe = show(
            component,
            data,
            width,
            height,
            no_display=True,
        )
        clear_output()
        display(button, iframe)

    watched_files = {
        name: name.stat().st_mtime for name in DIRECTORY.iterdir()
    }
    render()

    should_render = False
    with ui_events() as poll:
        while not stop:
            # We render only a second after a detected change.
            # This way we don't get double renders if multiple files change
            # shortly after eachother.
            if should_render:
                OPEN_WIDGETS[-1].close()
                del OPEN_WIDGETS[-1]
                render()
                should_render = False

            # Update the modified times of direct child files.
            for name, old_mtime in watched_files.items():
                if not name.exists():
                    continue

                new_mtime = name.stat().st_mtime
                if new_mtime == old_mtime:
                    continue
                watched_files[name] = new_mtime
                should_render = True

            # Allow jupyter to process UI interactions for a bit.
            t = time.time()
            while not stop and time.time() - t < 1.0:
                poll(10)


def clean():
    """Delete all temporary html files containing the widgets."""
    global OPEN_WIDGETS
    for w in OPEN_WIDGETS:
        w.close()
    OPEN_WIDGETS = []


def serve(directory, port, verbose):
    server_address = ('', port)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def end_headers(self):
            self.send_my_headers()
            SimpleHTTPRequestHandler.end_headers(self)

        def send_my_headers(self):
            self.send_header(
                "Cache-Control",
                "no-cache, no-store, must-revalidate"
            )
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

    if verbose:
        httpd = HTTPServer(server_address, Handler)

    else:
        class SilentHandler(Handler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

            def log_message(self, *_):
                return

        httpd = HTTPServer(server_address, SilentHandler)

    httpd.serve_forever()


atexit.register(clean)
