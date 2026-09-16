/*
 * PD3board Financial Workstation Controller & WebSocket Client
 * Full Bloomberg Professional Service Workstation Experience
 */

class SoundEngine {
  constructor() {
    this.enabled = false;
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
  }

  playKeyClick() {
    if (!this.enabled || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(800, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(120, this.ctx.currentTime + 0.03);
      gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.035);
    } catch (e) {}
  }

  playGoSound() {
    if (!this.enabled || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(520, this.ctx.currentTime);
      osc.frequency.setValueAtTime(1040, this.ctx.currentTime + 0.04);
      gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.09);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.1);
    } catch (e) {}
  }

  playChime() {
    if (!this.enabled || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1760, this.ctx.currentTime);
      gain.gain.setValueAtTime(0.05, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.18);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.2);
    } catch (e) {}
  }
}

class TerminalController {
  constructor() {
    this.ws = null;
    this.currentTicker = 'BTCUSDT';
    this.currentSector = 'CRNCY';
    this.currentFunction = 'GP';
    this.ticksCount = 0;
    this.clockMode = 'EST';
    this.sound = new SoundEngine();

    this.priceChart = null;
    this.orderBookUI = null;

    this.initUI();
    this.initWebSocket();
    this.initClock();
  }

  initUI() {
    this.cmdInput = document.getElementById('commandInput');
    this.priceChart = new PriceChart('priceCanvas');
    this.orderBookUI = new OrderBookUI('orderbookContainer');

    // Interval Selector Buttons
    document.querySelectorAll('.btn-interval').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-interval').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (this.priceChart) {
          this.priceChart.setInterval(btn.dataset.interval);
        }
        this.sound.playKeyClick();
      });
    });

    // Handle Enter on command input
    if (this.cmdInput) {
      this.cmdInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          this.executeCommand(this.cmdInput.value);
        } else {
          this.sound.playKeyClick();
        }
      });
    }

    // Global keyboard listener
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== this.cmdInput) {
        e.preventDefault();
        this.cmdInput.focus();
        this.cmdInput.select();
        this.sound.playKeyClick();
      } else if (e.key === 'Escape') {
        if (!document.getElementById('terminalModal').classList.contains('hidden')) {
          this.closeModal();
        } else if (this.cmdInput) {
          this.cmdInput.value = '';
          this.cmdInput.blur();
        }
        this.sound.playKeyClick();
      }
    });

    // Wire Sector Buttons
    document.querySelectorAll('.btn-sector').forEach(btn => {
      btn.addEventListener('click', () => {
        const sector = btn.dataset.sector;
        if (this.cmdInput) {
          this.cmdInput.value += ` ${sector}`;
          this.cmdInput.focus();
        }
        this.sound.playKeyClick();
      });
    });

    // Action buttons: GO and CNCL
    const btnGo = document.getElementById('btnGo');
    if (btnGo) {
      btnGo.addEventListener('click', () => {
        if (this.cmdInput) this.executeCommand(this.cmdInput.value);
      });
    }

    const btnCancel = document.getElementById('btnCancel');
    if (btnCancel) {
      btnCancel.addEventListener('click', () => {
        if (this.cmdInput) this.cmdInput.value = '';
        this.closeModal();
        this.sound.playKeyClick();
      });
    }

    // Wire Function Tabs
    document.querySelectorAll('.fn-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const fn = tab.dataset.fn;
        this.setFunction(fn);
        this.executeFunction(fn);
        this.sound.playKeyClick();
      });
    });

    // Modal Close Button
    const modalClose = document.getElementById('modalClose');
    if (modalClose) {
      modalClose.addEventListener('click', () => {
        this.closeModal();
        this.sound.playKeyClick();
      });
    }

    // Footer Toggle Controls
    const toggleAudio = document.getElementById('toggleAudio');
    if (toggleAudio) {
      toggleAudio.addEventListener('click', () => {
        this.sound.init();
        this.sound.enabled = !this.sound.enabled;
        toggleAudio.innerText = `AUDIO: ${this.sound.enabled ? 'ON' : 'OFF'}`;
        toggleAudio.classList.toggle('active', this.sound.enabled);
        if (this.sound.enabled) this.sound.playGoSound();
      });
    }

    const toggleCrt = document.getElementById('toggleCrt');
    const crtOverlay = document.getElementById('crtOverlay');
    if (toggleCrt && crtOverlay) {
      toggleCrt.addEventListener('click', () => {
        const isVisible = crtOverlay.style.display !== 'none';
        crtOverlay.style.display = isVisible ? 'none' : 'block';
        toggleCrt.innerText = `CRT: ${isVisible ? 'OFF' : 'ON'}`;
        toggleCrt.classList.toggle('active', !isVisible);
        this.sound.playKeyClick();
      });
    }

    const toggleClock = document.getElementById('toggleClock');
    const terminalClock = document.getElementById('terminalClock');
    const switchClock = () => {
      this.clockMode = this.clockMode === 'EST' ? 'UTC' : 'EST';
      if (toggleClock) toggleClock.innerText = `TIME: ${this.clockMode}`;
      this.sound.playKeyClick();
    };
    if (toggleClock) toggleClock.addEventListener('click', switchClock);
    if (terminalClock) terminalClock.addEventListener('click', switchClock);
  }

  initClock() {
    const clockEl = document.getElementById('terminalClock');
    const updateTime = () => {
      const now = new Date();
      if (clockEl) {
        if (this.clockMode === 'UTC') {
          clockEl.innerText = now.toISOString().substring(11, 19) + ' UTC';
        } else {
          // EST format
          clockEl.innerText = now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour12: false }) + ' EST';
        }
      }
    };
    updateTime();
    setInterval(updateTime, 1000);
  }

  initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stream`;
    const latencyEl = document.getElementById('wsLatency');

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      if (latencyEl) latencyEl.innerText = 'WS: 12ms';
      this.loadHistoricalData(this.currentTicker);
      this.loadOrderBook(this.currentTicker);
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.handleStreamMessage(msg);
      } catch (err) {
        console.error('Error handling WebSocket message:', err);
      }
    };

    this.ws.onclose = () => {
      if (latencyEl) latencyEl.innerText = 'WS: DISCONNECTED';
      setTimeout(() => this.initWebSocket(), 3000);
    };
  }

  handleStreamMessage(msg) {
    this.ticksCount++;
    const tickEl = document.getElementById('tickCounter');
    if (tickEl) tickEl.innerText = `TICKS: ${this.ticksCount}`;

    if (msg.type === 'tick') {
      if (msg.symbol === this.currentTicker) {
        this.updateHeaderPrice(msg.price, msg.side);
        if (this.priceChart) {
          this.priceChart.updateLiveTick(msg.price, msg.size);
        }
      }
    } else if (msg.type === 'depth') {
      if (msg.symbol === this.currentTicker && this.orderBookUI) {
        this.orderBookUI.update(msg.data);
        this.updateHeaderSpread(msg.data);
      }
    } else if (msg.type === 'wei') {
      this.renderWEI(msg.data);
    } else if (msg.type === 'equities_update') {
      this.updateEquitiesTicks(msg.data);
      if (Array.isArray(msg.data)) {
        msg.data.forEach(t => {
          if (t.symbol === this.currentTicker) {
            this.updateHeaderPrice(t.price, t.change >= 0 ? 'buy' : 'sell');
            if (this.priceChart) {
              this.priceChart.updateLiveTick(t.price, 100);
            }
          }
        });
      }
    } else if (msg.type === 'news') {
      this.renderNews(msg.data);
      this.sound.playChime();
    } else if (msg.type === 'yield_curve') {
      this.renderYieldCurve(msg.data);
    }
  }

  updateHeaderSpread(ob) {
    const spreadEl = document.getElementById('headerSpread');
    if (!spreadEl || !ob || !ob.bids || !ob.asks || !ob.bids.length || !ob.asks.length) return;
    const bestBid = ob.bids[0].price.toFixed(2);
    const bestAsk = ob.asks[0].price.toFixed(2);
    spreadEl.innerText = `${bestBid} / ${bestAsk}`;
  }

  async loadHistoricalData(ticker) {
    try {
      const res = await fetch(`/api/ticks/${ticker}`);
      if (res.ok) {
        const data = await res.json();
        if (this.priceChart && data.candles) {
          this.priceChart.setData(ticker, data.candles);
          if (data.candles.length > 0) {
            const last = data.candles[data.candles.length - 1];
            this.updateHeaderPrice(last.close, 'buy');
          }
        }
      }
    } catch (e) {
      console.warn('Could not load ticks:', e);
    }
  }

  async loadOrderBook(ticker) {
    try {
      const res = await fetch(`/api/orderbook/${ticker}`);
      if (res.ok) {
        const data = await res.json();
        if (this.orderBookUI && data && data.bids && this.currentTicker === ticker) {
          this.orderBookUI.update(data);
          this.updateHeaderSpread(data);
        }
      }
    } catch (e) {
      console.warn('Could not load orderbook:', e);
    }
  }

  async executeCommand(rawCommand) {
    if (!rawCommand || !rawCommand.trim()) return;
    this.sound.playGoSound();
    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: rawCommand })
      });
      const resp = await res.json();
      if (resp.success) {
        const { ticker, sector, function: fn } = resp.parsed;
        if (ticker) this.currentTicker = ticker;
        if (sector) this.currentSector = sector;
        if (fn) {
          this.setFunction(fn);
          this.executeFunction(fn, resp.data);
        }

        // Update Header
        const symbolBadge = document.getElementById('activeSymbol');
        if (symbolBadge) symbolBadge.innerText = `${this.currentTicker} ${this.currentSector}`;

        this.loadHistoricalData(this.currentTicker);
        this.loadOrderBook(this.currentTicker);
        if (this.cmdInput) this.cmdInput.value = '';
      }
    } catch (err) {
      console.error('Command execution failed:', err);
    }
  }

  setFunction(fn) {
    this.currentFunction = fn;
    document.querySelectorAll('.fn-tab').forEach(t => {
      t.classList.toggle('active', t.dataset.fn === fn);
    });
  }

  async executeFunction(fn, data = null) {
    if (fn === 'DES') {
      if (!data) {
        const res = await fetch(`/api/des/${this.currentTicker}`);
        data = res.ok ? await res.json() : null;
      }
      this.showDesModal(data);
    } else if (fn === 'HELP') {
      if (!data) {
        const res = await fetch('/api/help');
        data = res.ok ? await res.json() : null;
      }
      this.showHelpModal(data);
    } else if (fn === 'ECO') {
      if (!data) {
        const res = await fetch('/api/eco');
        data = res.ok ? await res.json() : null;
      }
      this.showEcoModal(data);
    } else {
      this.closeModal();
    }
  }

  showDesModal(des) {
    if (!des) return;
    const modal = document.getElementById('terminalModal');
    const heading = document.getElementById('modalHeading');
    const badge = document.getElementById('modalBadge');
    const body = document.getElementById('modalBody');

    badge.innerText = 'DES';
    heading.innerText = `${des.symbol} ${des.sector} // SECURITY DESCRIPTION & FUNDAMENTALS`;

    const isPos = des.change >= 0;
    const sign = isPos ? '+' : '';
    const chgClass = isPos ? 'pos' : 'neg';

    body.innerHTML = `
      <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid var(--border-amber); padding-bottom: 6px;">
        <div>
          <span style="font-size: 16px; font-weight: bold; color: var(--amber-bright);">${des.name}</span>
          <span class="neu" style="margin-left: 8px;">[${des.exchange} | ${des.industry}]</span>
        </div>
        <div>
          <span style="font-size: 16px; font-weight: bold; color: #fff;">${Number(des.price).toFixed(2)} USD</span>
          <span class="${chgClass}" style="margin-left: 6px; font-weight: bold;">${sign}${Number(des.change).toFixed(2)} (${sign}${Number(des.change_pct).toFixed(2)}%)</span>
        </div>
      </div>

      <div class="des-grid">
        <div class="des-card">
          <div class="des-card-title">VALUATION &amp; CAPITAL STRUCTURE</div>
          <div class="des-row"><span class="des-label">MARKET CAP</span><span class="des-val">${des.market_cap}</span></div>
          <div class="des-row"><span class="des-label">SHARES OUT</span><span class="des-val">${des.shares_out}</span></div>
          <div class="des-row"><span class="des-label">P/E (TTM)</span><span class="des-val">${des.pe}</span></div>
          <div class="des-row"><span class="des-label">FORWARD P/E</span><span class="des-val">${des.fwd_pe}</span></div>
          <div class="des-row"><span class="des-label">DILUTED EPS</span><span class="des-val">${des.eps}</span></div>
        </div>

        <div class="des-card">
          <div class="des-card-title">PRICE PERFORMANCE &amp; RISK</div>
          <div class="des-row"><span class="des-label">52-WEEK RANGE</span><span class="des-val">${des.range_52w}</span></div>
          <div class="des-row"><span class="des-label">BETA (5Y MONTHLY)</span><span class="des-val">${des.beta}</span></div>
          <div class="des-row"><span class="des-label">DIVIDEND YIELD</span><span class="des-val">${des.div_yield}</span></div>
          <div class="des-row"><span class="des-label">EX-DIVIDEND DATE</span><span class="des-val">${des.ex_div_date}</span></div>
          <div class="des-row"><span class="des-label">CURRENCY</span><span class="des-val">${des.currency}</span></div>
        </div>

        <div class="des-card">
          <div class="des-card-title">FINANCIAL PROFILE (TTM)</div>
          <div class="des-row"><span class="des-label">REVENUE</span><span class="des-val">${des.revenue}</span></div>
          <div class="des-row"><span class="des-label">NET INCOME</span><span class="des-val">${des.net_income}</span></div>
          <div class="des-row"><span class="des-label">PRIMARY EXCHANGE</span><span class="des-val">${des.exchange}</span></div>
        </div>

        <div class="des-card">
          <div class="des-card-title">CORPORATE GOVERNANCE</div>
          <div class="des-row"><span class="des-label">EXECUTIVE LEADERSHIP</span><span class="des-val">${des.ceo}</span></div>
          <div class="des-row"><span class="des-label">GLOBAL HEADQUARTERS</span><span class="des-val">${des.hq}</span></div>
          <div class="des-row"><span class="des-label">SECTOR CLASSIFICATION</span><span class="des-val">${des.sector}</span></div>
        </div>
      </div>
      <div style="text-align: right; font-size: 10px; color: var(--text-muted);">
        PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
      </div>
    `;
    modal.classList.remove('hidden');
  }

  showHelpModal(helpData) {
    if (!helpData) return;
    const modal = document.getElementById('terminalModal');
    const heading = document.getElementById('modalHeading');
    const badge = document.getElementById('modalBadge');
    const body = document.getElementById('modalBody');

    badge.innerText = 'HELP';
    heading.innerText = 'BLOOMBERG TERMINAL MNEMONIC & COMMAND DIRECTORY';

    let funcsHtml = '';
    const funcs = helpData.functions || (helpData.help ? helpData.help.map(h => ({ mnemonic: h.mnemonic, desc: h.desc })) : []);
    funcs.forEach(f => {
      funcsHtml += `<tr><td><strong style="color: var(--amber-primary);">${f.mnemonic} &lt;GO&gt;</strong></td><td>${f.desc}</td></tr>`;
    });

    body.innerHTML = `
      <div style="margin-bottom: 10px; color: var(--amber-bright); font-weight: bold;">AVAILABLE FUNCTION MNEMONICS</div>
      <table class="modal-table" style="margin-bottom: 14px;">
        <thead><tr><th>COMMAND</th><th>FUNCTION DESCRIPTION</th></tr></thead>
        <tbody>${funcsHtml}</tbody>
      </table>

      <div style="margin-bottom: 10px; color: var(--amber-bright); font-weight: bold;">KEYBOARD SHORTCUTS &amp; SYNTAX</div>
      <table class="modal-table">
        <thead><tr><th>SHORTCUT / KEY</th><th>WORKSTATION ACTION</th></tr></thead>
        <tbody>
          <tr><td><strong>/</strong></td><td>Focus Bloomberg command line prompt immediately</td></tr>
          <tr><td><strong>&lt;ESC&gt;</strong></td><td>Clear input buffer or dismiss current modal dialog</td></tr>
          <tr><td><strong>&lt;GO&gt; / Enter</strong></td><td>Execute entered mnemonic command</td></tr>
          <tr><td><strong>&lt;CNCL&gt;</strong></td><td>Cancel entered command line</td></tr>
          <tr><td><strong>&lt;TICKER&gt; [SECTOR] [FN] &lt;GO&gt;</strong></td><td>Standard Bloomberg command syntax (e.g. MCD US EQUITY GP &lt;GO&gt;)</td></tr>
        </tbody>
      </table>
      <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
        PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
      </div>
    `;
    modal.classList.remove('hidden');
  }

  showEcoModal(ecoData) {
    if (!ecoData) return;
    const modal = document.getElementById('terminalModal');
    const heading = document.getElementById('modalHeading');
    const badge = document.getElementById('modalBadge');
    const body = document.getElementById('modalBody');

    badge.innerText = 'ECO';
    heading.innerText = 'GLOBAL ECONOMIC CALENDAR & MACRO RELEASES';

    const events = ecoData.events || (Array.isArray(ecoData) ? ecoData : []);
    let rowsHtml = '';
    events.forEach(e => {
      const impClass = e.impact === 'HIGH' ? 'impact-high' : (e.impact === 'MED' ? 'impact-med' : 'impact-low');
      rowsHtml += `
        <tr>
          <td>${e.time}</td>
          <td><strong>${e.country}</strong></td>
          <td>${e.indicator}</td>
          <td>${e.period}</td>
          <td><strong>${e.actual}</strong></td>
          <td class="neu">${e.consensus}</td>
          <td class="neu">${e.prior}</td>
          <td><span class="impact-badge ${impClass}">${e.impact}</span></td>
        </tr>
      `;
    });

    body.innerHTML = `
      <table class="modal-table">
        <thead>
          <tr>
            <th>TIME</th>
            <th>CTRY</th>
            <th>INDICATOR</th>
            <th>PERIOD</th>
            <th>ACTUAL</th>
            <th>CONSENSUS</th>
            <th>PRIOR</th>
            <th>IMPACT</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
      <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
        PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
      </div>
    `;
    modal.classList.remove('hidden');
  }

  closeModal() {
    const modal = document.getElementById('terminalModal');
    if (modal) modal.classList.add('hidden');
    if (this.currentFunction === 'DES' || this.currentFunction === 'HELP' || this.currentFunction === 'ECO') {
      this.setFunction('GP');
    }
  }

  updateHeaderPrice(price, side) {
    const priceEl = document.getElementById('livePrice');
    if (!priceEl) return;
    priceEl.innerText = Number(price).toFixed(2);
    priceEl.className = side === 'buy' ? 'tick-up' : 'tick-down';
    setTimeout(() => { priceEl.className = ''; }, 350);
  }

  renderWEI(indices) {
    const tbody = document.getElementById('weiBody');
    if (!tbody || !indices) return;
    let html = '';
    indices.forEach(idx => {
      const isPos = idx.change >= 0;
      const cls = isPos ? 'pos' : 'neg';
      const sign = isPos ? '+' : '';
      html += `
        <tr id="row-${idx.symbol}" data-symbol="${idx.symbol}">
          <td><strong>${idx.symbol}</strong></td>
          <td class="neu">${idx.name}</td>
          <td class="text-right" id="price-${idx.symbol}">${idx.price.toFixed(2)}</td>
          <td class="text-right ${cls}" id="chg-${idx.symbol}">${sign}${idx.change.toFixed(2)}</td>
          <td class="text-right ${cls}" id="pct-${idx.symbol}">${sign}${idx.change_pct.toFixed(2)}%</td>
        </tr>
      `;
    });
    tbody.innerHTML = html;

    // Attach row click to load security
    tbody.querySelectorAll('tr').forEach(row => {
      row.addEventListener('click', () => {
        const sym = row.dataset.symbol;
        if (sym) {
          this.executeCommand(`${sym} INDEX GP <GO>`);
        }
      });
    });
  }

  updateEquitiesTicks(ticks) {
    ticks.forEach(t => {
      const priceEl = document.getElementById(`price-${t.symbol}`);
      const chgEl = document.getElementById(`chg-${t.symbol}`);
      const pctEl = document.getElementById(`pct-${t.symbol}`);
      if (priceEl && chgEl && pctEl) {
        const isPos = t.change >= 0;
        const cls = isPos ? 'pos' : 'neg';
        const sign = isPos ? '+' : '';
        priceEl.innerText = t.price.toFixed(2);
        priceEl.className = `text-right ${isPos ? 'tick-up' : 'tick-down'}`;
        setTimeout(() => { priceEl.className = 'text-right'; }, 350);
        chgEl.className = `text-right ${cls}`;
        chgEl.innerText = `${sign}${t.change.toFixed(2)}`;
        pctEl.className = `text-right ${cls}`;
        pctEl.innerText = `${sign}${t.change_pct.toFixed(2)}%`;
      }
    });
  }

  renderNews(newsItems) {
    const list = document.getElementById('newsList');
    if (!list || !newsItems) return;
    let html = '';
    newsItems.forEach(n => {
      html += `
        <div class="news-item">
          <div class="news-time">${n.time}</div>
          <div class="news-ticker">${n.ticker}</div>
          <div class="news-headline">${n.headline}</div>
          <div class="news-tag neu">${n.source}</div>
        </div>
      `;
    });
    list.innerHTML = html;
  }

  renderYieldCurve(curve) {
    const container = document.getElementById('yieldCurveData');
    if (!container || !curve) return;
    let html = `
      <div style="font-size: 11px; margin-bottom: 6px;">
        <span>2Y/10Y SPREAD: <strong class="${curve.inverted ? 'neg' : 'pos'}">${curve.spread_2_10_bps} BPS</strong></span>
        ${curve.inverted ? '<span class="neg" style="margin-left: 8px;">[INVERTED]</span>' : ''}
      </div>
      <table class="terminal-table">
        <thead>
          <tr><th>TENOR</th><th class="text-right">YIELD</th><th class="text-right">CHG</th></tr>
        </thead>
        <tbody>
    `;
    curve.tenors.forEach(t => {
      const cls = t.change >= 0 ? 'pos' : 'neg';
      const sign = t.change >= 0 ? '+' : '';
      html += `
        <tr>
          <td>${t.tenor}</td>
          <td class="text-right"><strong>${t.yield.toFixed(2)}%</strong></td>
          <td class="text-right ${cls}">${sign}${t.change.toFixed(2)}</td>
        </tr>
      `;
    });
    html += `</tbody></table>`;
    container.innerHTML = html;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.terminal = new TerminalController();
});
