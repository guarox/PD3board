/*
 * PD3board Financial Workstation Controller & WebSocket Client
 */

class TerminalController {
  constructor() {
    this.ws = null;
    this.currentTicker = 'BTCUSDT';
    this.currentSector = 'CRNCY';
    this.currentFunction = 'GP';
    this.ticksCount = 0;
    this.priceChart = null;
    this.orderBookUI = null;
    
    this.initUI();
    this.initWebSocket();
    this.initClock();
  }

  initUI() {
    this.cmdInput = document.getElementById('cmdInput');
    this.priceChart = new PriceChart('priceCanvas');
    this.orderBookUI = new OrderBookUI('orderbookContainer');

    // Handle Enter on command input
    this.cmdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        this.executeCommand(this.cmdInput.value);
      }
    });

    // Global keyboard listener: press '/' to focus command bar, Esc to cancel
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== this.cmdInput) {
        e.preventDefault();
        this.cmdInput.focus();
        this.cmdInput.select();
      } else if (e.key === 'Escape') {
        this.cmdInput.value = '';
        this.cmdInput.blur();
      }
    });

    // Wire Sector and Action Buttons
    document.querySelectorAll('.btn-key').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        const val = btn.dataset.val;
        if (action === 'sector') {
          this.cmdInput.value += ` ${val}`;
          this.cmdInput.focus();
        } else if (action === 'go') {
          this.executeCommand(this.cmdInput.value);
        } else if (action === 'cancel') {
          this.cmdInput.value = '';
        }
      } );
    });

    // Wire Function Tabs
    document.querySelectorAll('.fn-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const fn = tab.dataset.fn;
        this.setFunction(fn);
      });
    });
  }

  initClock() {
    const clockEl = document.getElementById('liveClock');
    const updateTime = () => {
      const now = new Date();
      if (clockEl) {
        clockEl.innerText = now.toTimeString().split(' ')[0] + ' EST';
      }
    };
    updateTime();
    setInterval(updateTime, 1000);
  }

  initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stream`;
    const latencyEl = document.getElementById('wsLatency');
    let lastPing = Date.now();

    console.log('Connecting to WebSocket:', wsUrl);
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('PD3board Stream Connected');
      if (latencyEl) latencyEl.innerText = 'WS: 12ms';
      this.loadHistoricalData(this.currentTicker);
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
      console.warn('WebSocket disconnected. Reconnecting in 3s...');
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
      }
    } else if (msg.type === 'wei') {
      this.renderWEI(msg.data);
    } else if (msg.type === 'equities_update') {
      this.updateEquitiesTicks(msg.data);
    } else if (msg.type === 'news') {
      this.renderNews(msg.data);
    } else if (msg.type === 'yield_curve') {
      this.renderYieldCurve(msg.data);
    }
  }

  async loadHistoricalData(ticker) {
    try {
      const res = await fetch(`/api/ticks/${ticker}`);
      if (res.ok) {
        const data = await res.json();
        if (this.priceChart && data.candles) {
          this.priceChart.setData(ticker, data.candles);
        }
      }
    } catch (e) {
      console.warn('Could not load ticks:', e);
    }
  }

  async executeCommand(rawCommand) {
    if (!rawCommand || !rawCommand.trim()) return;
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
        if (fn) this.setFunction(fn);

        // Update Header
        const symbolBadge = document.getElementById('activeSymbol');
        if (symbolBadge) symbolBadge.innerText = `${this.currentTicker} ${this.currentSector}`;

        this.loadHistoricalData(this.currentTicker);
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

  updateHeaderPrice(price, side) {
    const priceEl = document.getElementById('livePrice');
    if (!priceEl) return;
    priceEl.innerText = price.toFixed(2);
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
        <tr id="row-${idx.symbol}">
          <td><strong>${idx.symbol}</strong></td>
          <td class="neu">${idx.name}</td>
          <td class="text-right" id="price-${idx.symbol}">${idx.price.toFixed(2)}</td>
          <td class="text-right ${cls}" id="chg-${idx.symbol}">${sign}${idx.change.toFixed(2)}</td>
          <td class="text-right ${cls}" id="pct-${idx.symbol}">${sign}${idx.change_pct.toFixed(2)}%</td>
        </tr>
      `;
    });
    tbody.innerHTML = html;
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
