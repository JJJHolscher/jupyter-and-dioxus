# Jupyter and Dioxus

This repo contains:

- The python package `dioxus_widget`, which can open custom elements made with dioxus in an jupyter notebook.
- An example rust project that creates custom elements with Dioxus.
- A demo for presenting custom elements from dioxus in a jupyter notebook.

## Run the Demo

```sh
git clone https://github.com/JJJHolscher/jupyter-and-dioxus
cd jupyter-and-dioxus
cargo install wasm-pack
wasm-pack build --target web
python -m venv .venv
. .venv/bin/activate
pip install jupyterlab
cd doc
jupyter lab
```

Your browser opens jupyter lab, you open `demo.ipynb` and you run all.
You should now get a screenshot like this:

![screenshot of the widget showing in the output of a code cell](fig/widget-screenshot.png)

Which means the demo worked.

## Workflow

1. You create a custom Dioxus element in Rust, using the `custom-elements` crate. See `src/main.rs` for how to do that.
2. Run `wasm-pack build --debug --target web` such that your custom elements is put into a bunch of js and wasm files in some directory (probably `YOUR_RUST_PACKAGE_ROOT/pkg`).
3. `pip install dioxus_widget` 
4. `import dioxus_widget; dioxus_widget.init(JS_PATH)` a server will launch. JS_PATH is the javascript file you'd normally import in the html module script for loading in the wasm. It's usually found at `YOUR_RUST_PACKAGE_ROOT/pkg/YOUR_RUST_PACKAGE_NAME.js` .
5. `dioxus_widget.show(CUSTOM_ELEMENT_TAG, INNER_HTML)`

tadaa, now you get an iframe into a document with `<custom_element_tag>inner_html</custom_element_tag>`.

6. `dioxus_web.close()` run this to remove temporary html files, only run this after you're done looking at your widgets.


## Q&A

> Why use the custom-elements crate and not just directly mount dioxus on elements with a particular id?

This way, in the future (not now), you can also the element from markdown with relatively elegant syntax.
What you're asking is definitely doable though, and I might add that if that proves extra beneficial.

> Why is the dioxus element inside an iframe?

Some bug in `dioxus_web` disallowed the instantiation of multiple dioxus elements in a single document. Once this is patched, I'll drop the iframes and you can then also access the element from markdown.

This will make this library far more convenient, since `dioxus_widget` won't need to launch a server anymore or create temporary files.

> What is that doc/_quarto.yml?

[Quarto](quarto.org) allows you to convert markdown(-like) files into a website (or book, or article). The rad thing is that Quarto runs any code cells in the markdown.
At some point I will also test whether the dioxus widgets work in quarto-generated files.

> Does my notebook file need to be on the same device as the wasm and javascript that was generated by dioxus?

Yea, though not really.  
I made this library assuming you have the files locally so out of the box you won't be able to link to remote files when calling `dioxus_widget.init`.  
But it would be simpler if the dioxus-generated files are served from an already-existing separate server.
There's a decent chance I'll implement this simple change at some point, though for my personal use I won't need to now.

> Will you support custom elements that were made by different front-end libraries, like Yew or React?

Probably not since I don't plan to use other libraries. If I do, then they'll probably become included here.  
Also I will probably add them if you pay me.
