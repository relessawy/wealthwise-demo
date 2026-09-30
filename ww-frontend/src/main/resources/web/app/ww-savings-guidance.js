import { LitElement, html, css } from 'lit';

class WwSavingsGuidance extends LitElement {
  static properties = { result: {state: true}, error: {state: true}, busy: {state: true} };
  static styles = css`
    :host { display:block; max-width:960px; margin:0 auto; padding:24px; color:#283859; }
    .panel { border:1px solid #dce3ec; border-radius:18px; background:#fff; padding:28px; box-shadow:0 8px 30px #2838590a; }
    .eyebrow { text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; font-weight:700; color:#746437; }
    h1 { margin:8px 0; } p { line-height:1.6; } .muted { color:#5c687a; }
    form { display:flex; gap:18px; flex-wrap:wrap; align-items:end; margin:24px 0; }
    label { display:flex; flex-direction:column; gap:8px; font-weight:600; }
    input { box-sizing:border-box; width:170px; border:1px solid #a9b5c8; border-radius:8px; padding:12px; font:inherit; }
    button { border:0; border-radius:8px; padding:14px 22px; background:#283859; color:white; font:inherit; cursor:pointer; }
    button:disabled { opacity:.6; cursor:wait; } :focus-visible { outline:3px solid #b2a06a; outline-offset:3px; }
    .result { background:#f1f6fb; border-radius:12px; padding:24px; border-left:4px solid #b2a06a; }
    .amount { font-size:2.5rem; font-weight:700; } .error { color:#9c2525; }
    a { color:#284f80; } .links { margin-top:22px; } .disclaimer { font-size:.85rem; }
  `;
  constructor() { super(); this.result=null; this.error=''; this.busy=false; }
  async calculate(event) {
    event.preventDefault(); this.busy=true; this.error=''; this.result=null;
    const data=new FormData(event.target);
    try {
      const response=await fetch('/api/savings-guidance?'+new URLSearchParams(data), {headers:{'Accept':'application/json','X-Requested-With':'XMLHttpRequest'}});
      if (response.status===401 || response.redirected) throw new Error('Sign in to WealthWise, then calculate again.');
      if (!response.ok) throw new Error(response.status===400 ? 'Check the amounts and number of months.' : 'The calculator is temporarily unavailable. Please retry.');
      this.result=await response.json();
    } catch(error) { this.error=error.message; } finally { this.busy=false; }
  }
  render() {
    return html`<section class="panel" aria-labelledby="savings-title">
      <div class="eyebrow">ACME Bank · Savings planner</div><h1 id="savings-title">Make your goal a monthly habit</h1>
      <p class="muted">Explore a simple savings goal using illustrative amounts. This calculator does not use your account or chat history.</p>
      <form @submit=${this.calculate}>
        <label>Target amount<input name="target" type="number" min="0" max="10000000" step="0.01" value="1200.00" required></label>
        <label>Already saved<input name="saved" type="number" min="0" max="10000000" step="0.01" value="300.00" required></label>
        <label>Months<input name="months" type="number" min="1" max="120" step="1" value="6" required></label>
        <button type="submit" ?disabled=${this.busy}>${this.busy ? 'Calculating…' : 'Calculate my goal'}</button>
      </form>
      <div aria-live="polite" aria-busy=${this.busy}>${this.error ? html`<p class="error" role="alert">${this.error}</p>` : ''}
      ${this.result ? html`<div class="result"><div class="muted">Monthly contribution</div>
        <div class="amount">${Number(this.result.monthlyContribution).toFixed(2)}</div>
        <p><strong>${this.result.guidance}</strong></p><p class="disclaimer">${this.result.disclaimer}</p></div>` : ''}</div>
      <p class="links"><a href="/q/swagger-ui/" target="_blank" rel="noopener" router-ignore>Explore this API in Swagger UI ↗</a></p>
    </section>`;
  }
}
customElements.define('ww-savings-guidance', WwSavingsGuidance);
