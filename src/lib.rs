mod component;
use component::App;

use core::ops::Deref;
use dioxus::prelude::*;
use wasm_bindgen::prelude::*;
use web_sys::HtmlElement;

pub trait DioxusInElement: Sized + 'static {
    fn new(root: &HtmlElement) -> Self;
    fn root_component(cx: Scope<Self>) -> Element;
    fn launch(root: &HtmlElement) {
        dioxus_web::launch_with_props(
            Self::root_component,
            Self::new(root),
            dioxus_web::Config::new().rootelement(root.deref().clone()),
        );
    }
}

#[derive(Props, PartialEq)]
#[allow(non_camel_case_types)]
struct ExampleApp {
    inner_text: String,
}

impl DioxusInElement for ExampleApp {
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
pub fn example_app(root: &HtmlElement) {
    ExampleApp::launch(root);
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
