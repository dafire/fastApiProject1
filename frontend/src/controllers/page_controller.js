import {Controller} from "@hotwired/stimulus";
import {Toast} from 'bootstrap'

export default class extends Controller {

    static targets = ["toast", "toastArea"];


    themeSwitch = async (e) => {
        this.element.setAttribute(
            "data-bs-theme",
            e.target.checked ? "dark" : "light"
        );
        await fetch(e.params.url, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name: "darkmode", value: e.target.checked}),
        });
    };

    toast() {
        this.addToast("Hello, Stimulus!", "Hello", "Stimulus");
    }

    connect() {
        console.log("Hello, Stimulus!")
    }

    addToastEvent(event) {
        console.log("addToastEvent", event, event.detail);
        const detail = event.detail ?? {};
        this.addToast(
            detail.message,
            detail.title,
            detail.subtitle,
            detail.headerClass
        );
    }

    addToast(message, title = "test", subtitle = "", header_class = "") {
        if (!this.hasToastAreaTarget) return console.error("No toast area found!");

        var titleTemplate = title
            ? `<div class="toast-header ${header_class}">
            <strong class="me-auto">${title}</strong>
            <small>${subtitle}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>`
            : "";
        var toastTemplate = `
        <div class="toast mb-3" data-page-target='toast' role="alert" aria-live="assertive" aria-atomic="true">
        ${titleTemplate}
        <div class="toast-body">${message}</div>
        </div>
        `.trim();
        this.toastAreaTarget.insertAdjacentHTML("beforeend", toastTemplate);
    }

    toastTargetConnected(element) {
        if (element.dataset.shown === "true") return;
        new Toast(element).show();
        element.addEventListener(
            "hidden.bs.toast",
            () => {
                element.remove();
            },
            {once: true}
        );
        element.setAttribute("data-shown", "true");
    }

}