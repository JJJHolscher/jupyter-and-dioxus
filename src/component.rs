use dioxus::prelude::*;
use dioxus_core::RenderReturn;

// Define the Hackernews types
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use web_sys::{console, HtmlElement};

#[component]
pub fn App(cx: Scope, inner_text: String) -> Element {
    let mut count = use_state(cx, || 0);

    cx.render(rsx! {
        h1 { "{inner_text}: {count}" }
        button { onclick: move |_| count += 1, "Up high!" }
        button { onclick: move |_| count -= 1, "Down low!" }
    })
}
