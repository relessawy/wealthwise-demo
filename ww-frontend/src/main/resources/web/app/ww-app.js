import { LitElement, html, css } from 'lit';
import { Router } from '@vaadin/router';
import './ww-header.js';
import './ww-financial-advisor.js';
import './ww-investment-recommendations.js';
import './ww-footer.js';
import './ww-history.js';

class WwApp extends LitElement {
    static styles = css`
        :host {
            display: flex;
            flex-direction: column;
            width: 100%;
            min-height: 100vh;
            justify-content: space-between;
            overflow: auto;
        }
        .center {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            min-height: 420px;
        }

        nav {
            display: flex;
            justify-content: center;
            padding: 1rem;
            gap: clamp(0.25rem, 2vw, 2rem);
            flex-wrap: wrap;
        }
        a {
            text-decoration: none;
            color: var(--lumo-contrast-50);
            font-weight: bold;
            cursor: pointer;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: color 0.2s ease-in-out;
        }

        a:hover {
            color:#B2A06A;
        }

        a.active {
            background-color: rgb(40, 56, 89);
            color: white;
        }
        .content{
            overflow: scroll;
            max-height: 100%;
            height: 100%;
            margin-bottom: 20px;
        }
    `;

    static properties = {
        currentPath: { type: String },
        user: { state: true }
    };

    constructor() {
        super();
        this.currentPath = window.location.pathname;
        this.user = null;
    }

    firstUpdated() {
        fetch('/api/me', {headers: {'X-Requested-With':'XMLHttpRequest'}})
            .then(r => r.ok ? r.json() : null).then(u => { this.user = u; }).catch(() => {});
        const router = new Router(this.shadowRoot.querySelector('.content'));

        router.setRoutes([
            { path: '/', component: 'ww-financial-advisor' },
            { path: '/investment-recommendations', component: 'ww-investment-recommendations' },
            { path: '/history', component: 'ww-history' },
            { path: '(.*)', component: 'ww-financial-advisor' } // Default route / 404
        ]);

        // Listen for route changes
        window.addEventListener('vaadin-router-location-changed', () => {
            this.currentPath = window.location.pathname;
        });
    }

    _navigate(e) {
        e.preventDefault();
        const path = e.target.getAttribute('href');
        Router.go(path);
        this.currentPath = path;
    }

    render() {
        return html`
            <p>ACME Bank · Scripted demonstration, not live AI. ${this.user ? html`Signed in as ${this.user.username}. <a href="/logout" router-ignore>Sign out</a>` : html`<a href="/api/session" router-ignore>Sign in with your bank account</a>`}</p><div class="center">
                <ww-header></ww-header>
                <nav>
                    <a href="/"
                       @click=${this._navigate}
                       class="${this.currentPath === '/' ? 'active' : ''}">
                        Financial Advisor
                    </a>
                    <a href="/investment-recommendations"
                       @click=${this._navigate}
                       class="${this.currentPath === '/investment-recommendations' ? 'active' : ''}">
                        Investment Recommendations
                    </a>
                    <a href="/history"
                       @click=${this._navigate}
                       class="${this.currentPath === '/history' ? 'active' : ''}">
                        History
                    </a>
                </nav>
                <div class="content"></div>
            </div>
            <ww-footer></ww-footer>
        `;
    }
}

customElements.define('ww-app', WwApp);
