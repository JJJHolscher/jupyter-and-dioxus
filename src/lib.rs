mod component;
use component::App;

use core::ops::Deref;
use custom_elements::{inject_stylesheet, CustomElement};
use dioxus::prelude::*;
use wasm_bindgen::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::HtmlElement;

pub trait CustomDioxusElement {
    fn new(root: &HtmlElement);
    fn root_component(cx: Scope<Self>) -> Element;
}

impl<T: CustomDioxusElement + Default> CustomElement for T
{
    fn inject_children(&mut self, this: &HtmlElement) {
        self = CustomDioxusElement::new(this);

        dioxus_web::launch_with_props(
            self.root_component,
            self,
            dioxus_web::Config::new().rootelement(this.deref().clone()),
        );
    }

    fn shadow() -> bool {
        false
    }
}

#[derive(Props, PartialEq)]
#[allow(non_camel_case_types)]
struct ExampleApp {
    inner_text: String,
}

impl CustomDioxusElement for ExampleApp {
    fn new(root: &HtmlElement) -> Self {
        let inner_text = root.inner_text();
        root.set_inner_html("");
        ExampleApp { inner_text }
    }

    fn root_component(cx: Scope<Self>) -> Element {
        let mut count = use_state(cx, || 0);

        cx.render(rsx! {
            h1 { "{cx.props.inner_text}: {count}" }
            button { onclick: move |_| count += 1, "Up high!" }
            button { onclick: move |_| count -= 1, "Down low!" }
        })
    }
}

#[wasm_bindgen]
pub fn run() {
    ExampleApp::define("ce-dioxus");
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
