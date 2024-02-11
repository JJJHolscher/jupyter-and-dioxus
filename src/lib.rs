use dioxus::prelude::{dioxus_elements, rsx, use_state, Element, Props, Scope};
use wasm_bindgen::prelude::*;
use web_sys::HtmlElement;

// Implement this trait for a struct that holds any data you want to pass to your component
// function.
pub trait DioxusInElement: Sized + 'static {
    // Run code before launching dioxus.
    // Use this for modifying the HtmlElement beforehand and for extracting any data you want to pass
    // to your component.
    fn new(root: &HtmlElement) -> Self;
    // The root component function.
    fn component(cx: Scope<Self>) -> Element;
    fn launch(root: &HtmlElement) {
        dioxus_web::launch_with_props(
            Self::component,
            Self::new(root),
            dioxus_web::Config::new().rootname(root.id()),
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

    fn component(cx: Scope<Self>) -> Element {
        let mut count = use_state(cx, || 0);

        cx.render(rsx! {
            h1 { "{cx.props.inner_text}: {count}" }
            button { onclick: move |_| count += 1, "Up high!" }
            button { onclick: move |_| count -= 1, "Down low!" }
        })
    }
}

// The function that when called from javascript, launches your dioxus component on some element.
// Unfortunately you will probably always need to have a funtion like this.
// In the future there might be a macro that exposes this function for you if you implemented the
// DioxusInElement trait.
#[wasm_bindgen]
pub fn example_app(root: &HtmlElement) {
    ExampleApp::launch(root);
}
