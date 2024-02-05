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

impl CustomElement for ComponentWrapper {
    fn inject_children(&mut self, this: &HtmlElement) {
        let inner_text = this.inner_text();
        this.set_inner_html("");
        dioxus_web::launch_with_props(
            App,
            component::AppProps {
                inner_text: inner_text.to_owned(),
            },
            dioxus_web::Config::new().rootelement(this.deref().clone()),
        );
    }

    fn shadow() -> bool {
        false
    }
}

impl Default for ComponentWrapper {
    fn default() -> Self {
        Self::new()
    }
}

#[wasm_bindgen]
pub fn run() {
    ComponentWrapper::define("ce-dioxus");
    // let f = Closure::wrap(Box::new(move || {
    // ComponentWrapper::define("ce-dioxus");
    // }) as Box<dyn FnMut()>);

    // let win = web_sys::window().unwrap();
    // let _ = win.add_event_listener_with_callback("load", f.as_ref().unchecked_ref());

    // f.forget(); // It is not good practice, just for simplification!
}

#[wasm_bindgen]
pub fn change(id: String) {
    let element = web_sys::window()
        .unwrap()
        .document()
        .unwrap()
        .get_element_by_id(&id)
        .unwrap();
    let inner_text = element.inner_html();
    element.set_inner_html("");
    dioxus_web::launch_with_props(
        App,
        component::AppProps { inner_text },
        dioxus_web::Config::new().rootelement(element),
    );
}
