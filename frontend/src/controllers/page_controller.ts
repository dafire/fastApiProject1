import {Controller} from "@hotwired/stimulus"
// @ts-ignore
import {Toast} from "bootstrap/dist/js/bootstrap";

export default class PageController extends Controller {
    private static websocket?: WebSocket;
    private static reconnector?: NodeJS.Timeout;
    private static shouldReconnect: boolean;
    declare readonly websocketUrlValue: string
    declare readonly hasWebsocketUrlValue: boolean
    declare readonly hasToastAreaTarget: boolean
    declare readonly toastAreaTarget: HTMLDivElement
    declare readonly hasSocketStatusTarget: boolean
    declare readonly socketStatusTarget: HTMLLinkElement
    private openHandler: EventListener;
    private closeHandler: EventListener;
    private errorHandler: EventListener;
    private messageHandler: EventListener;

    connect() {
        if (this.hasWebsocketUrlValue) {
            PageController.shouldReconnect = true;
            if (!PageController.websocket) PageController.websocket = this.createWebsocket(); else this.websocketBindEvents(PageController.websocket);
        } else {
            PageController.shouldReconnect = false;
            if (PageController.websocket) PageController.websocket.close();
        }
    }

    static targets = ["toast", "toastArea", "socketStatus"];
    static values = {websocketUrl: String};

    toast() {
        this.addToast("Hello, Stimulus!", "Hello", "Stimulus");
    }

    addToastEvent(event: CustomEvent) {
        console.log("addToastEvent", event, event.detail);
        const detail = event.detail ?? {};
        this.addToast(detail.websocketOnMessage, detail.title, detail.subtitle, detail.headerClass);
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


    private websocketOnMessage(evt: MessageEvent) {
        console.log("Message received!", evt)
    }

    private websocketOnOpen() {
        console.log("Socket connected!");
        this.updateConnectionStatus();
    }

    private websocketOnError() {
        console.error("Socket error!");
        this.updateConnectionStatus();
    };

    private updateConnectionStatus() {
        if (this.hasSocketStatusTarget) {
            this.socketStatusTarget.classList.remove("bi-wifi-off", "bi-wifi");
            if (PageController.websocket) {
                switch (PageController.websocket.readyState) {
                    case WebSocket.OPEN:
                        this.socketStatusTarget.classList.add("bi-wifi");
                        break;
                    default:
                        this.socketStatusTarget.classList.add("bi-wifi-off");
                }
            }
        }
    }

    private websocketOnClose(event: CloseEvent) {
        this.websocketUnbindEvents(PageController.websocket);
        PageController.websocket = undefined
        if (PageController.shouldReconnect) {
            PageController.reconnector = setTimeout(() => {
                if (PageController.shouldReconnect) PageController.websocket = this.createWebsocket();
            }, 500);
        }
        this.updateConnectionStatus();
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
        this.messageHandler = this.websocketOnMessage.bind(this);
        socket.addEventListener("message", this.messageHandler);
    }

}