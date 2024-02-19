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
      import init, { COMPONENT } from "/PACKAGE";
      async function main() {
        await init();
        COMPONENT(document.getElementById("dioxus-component"));
      }
      main();
    </script>STYLE
  </head>
  <body>
    <div id="dioxus-component"ATTRIBUTES>DATA</div>
  </body>
</html>
"""
OPEN_WIDGETS = []
DIRECTORY = Path(".")
PORT = 0


def init(
    package_path: str,
    style_path: str = "",
    port: int = 8000,
    verbose: bool = False
):
    """Host the custom elements by specifying their location.

    ARGS:
        package_path: the path to a local javascript file that loads the wasm.
        style_path: the path to a css file for styling the widget. It only gets
            included if it exists and is a css file.
        port: the port this library's server will listen to.
        verbose: whether this server will print to stderr.
    """
    global TEMPLATE, SERVER, DIRECTORY, PORT

    # Link the template to the supplied package javascript file.
    package = Path(package_path)
    DIRECTORY = package.parent
    TEMPLATE = TEMPLATE.replace("PACKAGE", package_path)

    # Optionally link the template to a supplied css file.
    style = Path(style_path)
    if style_path and style_path[-4:] == ".css" and style.exists():
        TEMPLATE = TEMPLATE.replace(
            "STYLE", f'\n<link rel="stylesheet" href="/{style}">'
        )
    else:
        TEMPLATE = TEMPLATE.replace("STYLE", "")

    # Do cleanup of past `open` calls that weren't closed.
    for f in DIRECTORY.iterdir():
        if f.name[:27] == "__tmp_dioxus_widget_iframe_":
            f.unlink()

    # Host these resources on a separate http server to circumvent
    # https://github.com/DioxusLabs/dioxus/issues/1907
    PORT = port
    SERVER = threading.Thread(
        target=serve,
        name="http server",
        args=[port, verbose]
    )
    SERVER.start()
    return SERVER, TEMPLATE


def show(
    component: str,
    data: str,
    attr: dict = {},
    width=500,
    height=500,
    no_display=False,
):
    """Present the data through a dioxus component"""
    global OPEN_WIDGETS

    atttributes = "" if not attr else " " + "".join([
        f'{name}="{value}"' for name, value in attr.items()
    ])

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
        .replace("ATTRIBUTES", atttributes)
    )
    w.flush()
    OPEN_WIDGETS.append(w)

    url = f"http://localhost:{PORT}/{DIRECTORY / Path(w.name).name}"
    iframe = IFrame(url, width, height)
    if no_display:
        return iframe
    else:
        display(iframe)


def debug(
    component: str,
    data: str,
    attr: dict = {},
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
            attr,
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


def serve(port, verbose):
    server_address = ('', port)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

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
                super().__init__(*args, **kwargs)

            def log_message(self, *_):
                return

        httpd = HTTPServer(server_address, SilentHandler)

    httpd.serve_forever()


atexit.register(clean)
