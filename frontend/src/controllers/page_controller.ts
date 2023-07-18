import {Controller} from "@hotwired/stimulus"
// @ts-ignore
import {Toast} from "bootstrap/dist/js/bootstrap";

export default class PageController extends Controller {
    static targets = ["toast", "toastArea"];
    static values = {websocketUrl: String};
    private static websocket?: WebSocket;
    private static shouldReconnect: boolean;
    declare readonly websocketUrlValue: string
    declare readonly hasWebsocketUrlValue: boolean
    declare readonly hasToastAreaTarget: boolean
    declare readonly toastAreaTarget: HTMLDivElement
    private openHandler: EventListener;
    private closeHandler: EventListener;
    private errorHandler: EventListener;
    private messageHandler: EventListener;

    connect() {
        console.log("Hello, Stimulus!", this.hasWebsocketUrlValue, this.element);
        if (this.hasWebsocketUrlValue) {
            PageController.shouldReconnect = true;
            if (!PageController.websocket) PageController.websocket = this.createWebsocket();
            else this.websocketBindEvents(PageController.websocket);
        } else {
            PageController.shouldReconnect = false;
            if (PageController.websocket) PageController.websocket.close();
        }
    }

    toast() {
        this.addToast("Hello, Stimulus!", "Hello", "Stimulus");
    }

    addToastEvent(event: CustomEvent) {
        console.log("addToastEvent", event, event.detail);
        const detail = event.detail ?? {};
        this.addToast(detail.message, detail.title, detail.subtitle, detail.headerClass);
    }

    addToast(message: string, title = "test", subtitle = "", header_class = "") {
        if (!this.hasToastAreaTarget) return console.error("No toast area found!");

        var titleTemplate = title ? `<div class="toast-header ${header_class}">
            <strong class="me-auto">${title}</strong>
            <small>${subtitle}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>` : "";
        var toastTemplate = `
        <div class="toast mb-3" data-page-target='toast' role="alert" aria-live="assertive" aria-atomic="true">
        ${titleTemplate}
        <div class="toast-body">${message}</div>
        </div>
        `.trim();
        this.toastAreaTarget.insertAdjacentHTML("beforeend", toastTemplate);
    }

    toastTargetConnected(element: HTMLDivElement) {
        if (element.dataset.shown === "true") return;
        new Toast(element).show();
        element.addEventListener("hidden.bs.toast", () => {
            element.remove();
        }, {once: true});
        element.setAttribute("data-shown", "true");
    }

    private message(evt: MessageEvent) {
        console.log("Message received!", evt)
    }

    private websocketOnOpen() {
        console.log("Socket connected!");
    }

    private websocketOnError() {
        console.error("Socket error!");
    };

    private websocketOnClose(event: CloseEvent) {
        this.websocketUnbindEvents(PageController.websocket);
        console.log("Socket closed! Reconnecting ...", PageController.shouldReconnect);
        if (PageController.shouldReconnect) {
            PageController.websocket = this.createWebsocket();
        } else {
            PageController.websocket = undefined
        }

    };

    private createWebsocket() {
        let socket = new WebSocket(this.websocketUrlValue);
        this.websocketBindEvents(socket);
        return socket;
    }

    private websocketUnbindEvents(socket: WebSocket) {
        socket.removeEventListener("open", this.openHandler);
        socket.removeEventListener("close", this.closeHandler);
        socket.removeEventListener("error", this.errorHandler);
        socket.removeEventListener("message", this.messageHandler);
    }

    private websocketBindEvents(socket: WebSocket) {
        this.websocketUnbindEvents(socket);
        this.openHandler = this.websocketOnOpen.bind(this);
        socket.addEventListener("open", this.openHandler);
        this.closeHandler = this.websocketOnClose.bind(this);
        socket.addEventListener("close", this.closeHandler);
        this.errorHandler = this.websocketOnError.bind(this);
        socket.addEventListener("error", this.errorHandler);
        this.messageHandler = this.message.bind(this);
        socket.addEventListener("message", this.messageHandler);
    }

}