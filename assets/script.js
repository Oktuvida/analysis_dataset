let attach_event_to_dash = (id, event, callback, options) => {
    let observer = new MutationObserver((_mutations, obs) => {
        let ele = document.getElementById(id);
        if (ele) {
            ele.addEventListener(event, callback, options)
            obs.disconnect()
        }
    });
    window.addEventListener('DOMContentLoaded', () => {
        observer.observe(document, {
            childList: true,
            subtree: true
        })
    })
}

attach_event_to_dash("slider_btn", "click", () => {
    document.getElementById("slider_btn").classList.toggle("hide");
    document.getElementById("sidebar").classList.toggle("hide");
    document.getElementById("page_content").classList.toggle("full");
})

attach_event_to_dash("sidebar", "click", event => {
    let element = event.target;
    if (element.classList.contains("nav-link")) {
        [...document.querySelectorAll(".nav-link")].map(el => el !== element && el.classList.remove("active"))
        element.classList.add("active")

        let href = element.getAttribute("href")
        if (href === "#") {
            document.querySelector(".introduction").classList.remove("hide");
            [...document.querySelectorAll(".card_container")].map(el => el.classList.add("hide"));
            return;
        }

        element = document.querySelector(href)
        if (element) {
            [...document.querySelectorAll(".introduction")].map(el => el.classList.add("hide"));
            [...document.querySelectorAll(".card_container")].map(el => el.classList.add("hide"));
            element.classList.remove("hide");
        }
    }

})