mod component;
use component::App;

use core::ops::Deref;
use custom_elements::{inject_stylesheet, CustomElement};
use dioxus::prelude::*;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::HtmlElement;

struct ComponentWrapper {}

impl ComponentWrapper {
    fn new() -> Self {
        Self {}
    }
}

// #[derive(PartialEq, Props)]
// struct AppProps {
// inner_text: String,
// }

impl CustomElement for ComponentWrapper {
    fn inject_children(&mut self, this: &HtmlElement) {
        dioxus_web::launch_with_props(
            App,
            component::AppProps {
                inner_text: this.inner_html(),
                inner_html: "".to_owned(),
            },
            dioxus_web::Config::new().rootelement(this.deref().clone()),
        );
    }

    fn shadow() -> bool {
        false
    }

    fn connected_callback(&mut self, this: &HtmlElement) {
        this.inner_html();
    }
}

impl Default for ComponentWrapper {
    fn default() -> Self {
        Self::new()
    }
}

#[wasm_bindgen]
pub fn run() {
    let f = Closure::wrap(Box::new(move || {
        ComponentWrapper::define("ce-dioxus");
    }) as Box<dyn FnMut()>);
    // let f: Closure<FnMut()> = Closure::new(|| {
    // ComponentWrapper::define("ce-dioxus");
    // });
    // e.set_onresize(Some(f.as_ref().unchecked_ref()));

    let win = web_sys::window().unwrap();
    win.add_event_listener_with_callback("load", f.as_ref().unchecked_ref());

    f.forget(); // It is not good practice, just for simplification!
}
