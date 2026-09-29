import {LitElement, html, css} from 'lit';
import '@vaadin/icon';
import '@vaadin/vaadin-lumo-styles/vaadin-iconset.js';
import '@vaadin/icons';
import '@vaadin/button';
import '@vaadin/text-field';
import '@qomponent/qui-bubble';
import MarkdownIt from 'markdown-it';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';

class WwFinancialAdvisor extends LitElement {
    static styles = css`
        :host {
            display: flex;
            gap: 10px;
            flex-direction: column;
            align-items: center;
            height: 100%;
            padding-bottom: 20px;
        }
        .input {
            display: flex;
            gap: 10px;
            align-items: baseline;
            align-self: center;
            width: 100%;
            justify-content: space-around;
        }
        .input vaadin-text-field {
            width: 80%;
        }
        .input vaadin-button {
            width: 20%;
        }

        .chat-messages {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .advisor-message {
            --chat-bubble-bg:#A5C882;
        }
        .user-message{
            --chat-bubble-bg:#5AB1BB;
        }

        .advisor-message-inner{
            width: 100%;
        }
        .chat-container{
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 80%;
            gap: 10px;
        }
    `;

    static properties = {
        _question: {type: String},
        _pending: {state: true},
        _chatMessages: {type: Array},
    };

    constructor() {
        super();
        this._question = '';
        this._pending = false;
        this._chatMessages = [];
        this.md = new MarkdownIt({html: false, linkify: false});
    }

    connectedCallback() {
        super.connectedCallback();

        var _this = this;

        this.ajax = new XMLHttpRequest();
        this.ajax.timeout = 15000;
        this.ajax.addEventListener("load", function() { if (_this.ajax.status >= 200 && _this.ajax.status < 300) { try { _this.onAjaxLoad(); } catch(e) { _this.onAjaxError(); } } else { _this.onAjaxError(); } });
        this.ajax.addEventListener("error", () => this.onAjaxError());
        this.ajax.addEventListener("timeout", () => this.onAjaxError());
    }

    onAjaxError() { this._pending = false; this._replaceLastMessage({owner: "advisor", message: "Request failed. Check your sign-in and try again."}); }

    onAjaxLoad() {
        this._pending = false;
        var response = JSON.parse(this.ajax.responseText).message;
        const htmlContent = this.md.render(response);

        this._replaceLastMessage({owner: 'advisor', message: htmlContent});
        this.shadowRoot.querySelector('#input')?.focus();
    }

    disconnectedCallback() {
        super.disconnectedCallback();
    }

    render(){
        return html`
            <div class="chat-container">
                ${this._renderChatMessages()}
                ${this._renderInput()}
            </div>
        `;
    }

    firstUpdated(){
        this.shadowRoot.querySelector('#input')?.focus();
    }

    _renderInput(){
        return html`<div class="input">
                        <vaadin-text-field id="input"
                            placeholder="Ask me anything about your finances"
                            .value=${this._question}
                            @input=${this._handleInput}
                            @keypress=${this._handleKeyPress}>
                        </vaadin-text-field>
        <vaadin-button ?disabled=${this._pending || !this._question.trim()} @click=${this._ask}>Ask</vaadin-button></div>`;
    }

    _renderChatMessages(){
        if(this._chatMessages.length > 0){
            return html`<div class="chat-messages">${this._chatMessages.map(message => {
                if(message.owner === 'user'){
                    return html`<qui-bubble class="user-message" name="You" icon="/static/user.png">
                        <p>${message.message}</p>
                    </qui-bubble>`;
                }else if(message.owner === 'advisor'){
                    return html`<qui-bubble class="advisor-message" name="Advisor" icon="/static/logo.png">
                        <span class="advisor-message-inner">${unsafeHTML(message.message)}</span>
                    </qui-bubble>`;
                } else if(message.owner === 'loading'){
                    return html`<qui-bubble class="advisor-message" name="Advisor" icon="/static/logo.png" typing></qui-bubble>`;
                }

            })}</div>`;
        }
    }

    _ask(){
        if(this._pending || !this._question.trim()) return;
        this._pending=true;
        this._addToMessages({owner: 'user', message: this._question}, {owner: 'loading'});
        var data = { "message": this._question, "requestId": crypto.randomUUID() };
        this.ajax.open("POST", "/api/financial/chat", true);
        this.ajax.setRequestHeader("Content-Type", "application/json");
        this.ajax.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        this.ajax.send(JSON.stringify(data));
        this._question = '';
    }

    _handleInput(event){
        this._question = event.target.value;
    }

    _handleKeyPress(event){
        if(event.key === 'Enter'){
            this._ask();
        }
    }

    _addToMessages(...messages){
        this._chatMessages = [...this._chatMessages, ...messages];
        this._scrollToBottom();
    }

    _replaceLastMessage(newMessage) {
        if (this._chatMessages.length === 0) return;
        this._chatMessages.pop();
        this._addToMessages(newMessage);
        this._scrollToBottom();
    }

    _scrollToBottom() {
        const chatContainer = this.shadowRoot.querySelector('.chat-messages');
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
}
customElements.define('ww-financial-advisor', WwFinancialAdvisor);
