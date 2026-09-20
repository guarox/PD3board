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

    // Command History Memory
    this.cmdHistory = [];
    this.historyIdx = -1;

    this.priceChart = null;
    this.orderBookUI = null;
    this.marketSessions = { NYSE: 'CLOSED', LSE: 'CLOSED', TSE: 'OPEN', CRNCY: 'OPEN' };

    this.initUI();
    this.initWebSocket();
    this.initClock();
    this.updateMarketStatus(this.marketSessions);

    // Periodic background sync to keep candlestick chart aligned with server state
    setInterval(() => {
      if (this.priceChart && this.currentTicker && this.currentFunction === 'GP') {
        const activeInterval = this.priceChart.interval || '1M';
        fetch(`/api/ticks/${this.currentTicker}?interval=${activeInterval}`)
          .then(r => r.ok ? r.json() : null)
          .then(data => {
            if (data && data.candles && this.priceChart && this.currentFunction === 'GP') {
              this.priceChart.syncCandles(data.candles);
            }
          })
          .catch(() => {});
      }
    }, 20000);
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
        const interval = btn.dataset.interval;
        if (this.priceChart) {
          this.priceChart.setInterval(interval);
        }
        this.loadHistoricalData(this.currentTicker, interval);
        this.sound.playKeyClick();
      });
    });

    // Technical Indicator Selector Buttons
    document.querySelectorAll('.btn-indicator').forEach(btn => {
      btn.addEventListener('click', () => {
        const ind = btn.dataset.indicator;
        if (this.priceChart) {
          const active = this.priceChart.toggleIndicator(ind);
          btn.classList.toggle('active', active);
        }
        this.sound.playKeyClick();
      });
    });

    // Handle Enter and Up/Down Command Recall on command input
    if (this.cmdInput) {
      this.cmdInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          this.executeCommand(this.cmdInput.value);
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          if (this.cmdHistory.length > 0 && this.historyIdx < this.cmdHistory.length - 1) {
            this.historyIdx++;
            this.cmdInput.value = this.cmdHistory[this.cmdHistory.length - 1 - this.historyIdx];
          }
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          if (this.historyIdx > 0) {
            this.historyIdx--;
            this.cmdInput.value = this.cmdHistory[this.cmdHistory.length - 1 - this.historyIdx];
          } else if (this.historyIdx === 0) {
            this.historyIdx = -1;
            this.cmdInput.value = '';
          }
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

    const fetchMarketStatus = async () => {
      try {
        const res = await fetch('/api/market-status');
        if (res.ok) {
          const json = await res.json();
          if (json.data) this.updateMarketStatus(json.data, json.terminal_id);
        }
      } catch (e) {}
    };
    fetchMarketStatus();
    setInterval(fetchMarketStatus, 30000);
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

  isTickerMatch(s1, s2) {
    if (!s1 || !s2) return false;
    const norm1 = s1.toUpperCase().replace(/[-_]/g, '');
    const norm2 = s2.toUpperCase().replace(/[-_]/g, '');
    if (norm1 === norm2) return true;
    const aliases = [
      ['BTC', 'BTCUSD', 'BTCUSDT'],
      ['ETH', 'ETHUSD', 'ETHUSDT'],
      ['SOL', 'SOLUSD', 'SOLUSDT'],
      ['SPX', '^GSPC', 'SP500'],
      ['NDX', '^IXIC', 'NASDAQ100'],
      ['DJI', '^DJI', 'DOW']
    ];
    for (const group of aliases) {
      if (group.includes(norm1) && group.includes(norm2)) return true;
    }
    return false;
  }

  handleStreamMessage(msg) {
    this.ticksCount++;
    const tickEl = document.getElementById('tickCounter');
    if (tickEl) tickEl.innerText = `TICKS: ${this.ticksCount}`;

    if (msg.type === 'tick') {
      if (this.isTickerMatch(msg.symbol, this.currentTicker)) {
        this.updateHeaderPrice(msg.price, msg.side);
        if (this.priceChart) {
          this.priceChart.updateLiveTick(msg.price, msg.size, msg.timestamp);
        }
      }
    } else if (msg.type === 'depth') {
      if (this.isTickerMatch(msg.symbol, this.currentTicker) && this.orderBookUI) {
        this.orderBookUI.update(msg.data);
        this.updateHeaderSpread(msg.data);
      }
    } else if (msg.type === 'wei') {
      this.renderWEI(msg.data);
    } else if (msg.type === 'equities_update') {
      this.updateEquitiesTicks(msg.data);
      if (Array.isArray(msg.data)) {
        msg.data.forEach(t => {
          if (this.isTickerMatch(t.symbol, this.currentTicker)) {
            this.updateHeaderPrice(t.price, t.change >= 0 ? 'buy' : 'sell');
          }
        });
      }
    } else if (msg.type === 'news') {
      const isNew = this.lastNewsHeadline && msg.data && msg.data[0] && msg.data[0].headline !== this.lastNewsHeadline;
      this.renderNews(msg.data);
      if (isNew) {
        this.sound.playChime();
      }
      if (msg.data && msg.data[0]) {
        this.lastNewsHeadline = msg.data[0].headline;
      }
    } else if (msg.type === 'yield_curve') {
      this.renderYieldCurve(msg.data);
    } else if (msg.type === 'market_status') {
      this.updateMarketStatus(msg.data, msg.terminal_id);
    }
  }

  updateMarketStatus(sessions, terminalId = null) {
    if (terminalId) {
      const termEl = document.getElementById('terminalId');
      if (termEl) termEl.innerText = terminalId;
    }
    if (!sessions) return;
    this.marketSessions = sessions;
    const nyseEl = document.getElementById('mktNYSE');
    const lseEl = document.getElementById('mktLSE');
    const tseEl = document.getElementById('mktTSE');
    const crncyEl = document.getElementById('mktCRNCY');

    const setStatusClass = (el, text, status) => {
      if (!el) return;
      el.innerText = text;
      if (status === 'OPEN') {
        el.className = 'pos';
      } else if (status === 'AFTER-HOURS' || status === 'PRE-MARKET' || status === 'LUNCH') {
        el.className = 'cyan';
      } else {
        el.className = 'neu';
      }
    };

    if (nyseEl && sessions.NYSE) setStatusClass(nyseEl, `NYSE: ${sessions.NYSE}`, sessions.NYSE);
    if (lseEl && sessions.LSE) setStatusClass(lseEl, `LSE: ${sessions.LSE}`, sessions.LSE);
    if (tseEl && sessions.TSE) setStatusClass(tseEl, `TSE: ${sessions.TSE}`, sessions.TSE);
    if (crncyEl) setStatusClass(crncyEl, 'CRYPTO: 24/7', 'OPEN');

    this.updateActiveSecurityBadge();
  }

  updateActiveSecurityBadge() {
    const symbolBadge = document.getElementById('activeSymbol');
    if (!symbolBadge) return;
    const ticker = this.currentTicker ? this.currentTicker.toUpperCase() : 'BTCUSDT';
    const sector = this.currentSector ? this.currentSector.toUpperCase() : 'CRNCY';

    let statusText = '24/7';
    let statusClass = 'pos';

    if (['BTC', 'ETH', 'SOL', 'BTCUSD', 'BTCUSDT', 'ETHUSD', 'ETHUSDT', 'SOLUSD', 'SOLUSDT'].includes(ticker) || sector === 'CRNCY') {
      statusText = '24/7 LIVE';
      statusClass = 'pos';
    } else if (['N225', '^N225'].includes(ticker)) {
      const st = this.marketSessions?.TSE || 'CLOSED';
      statusText = st;
      statusClass = st === 'OPEN' ? 'pos' : (st === 'LUNCH' ? 'cyan' : 'neu');
    } else if (['FTSE', '^FTSE', 'DAX', '^GDAXI'].includes(ticker)) {
      const st = this.marketSessions?.LSE || 'CLOSED';
      statusText = st;
      statusClass = st === 'OPEN' ? 'pos' : 'neu';
    } else {
      // US Equities and Indices
      const st = this.marketSessions?.NYSE || 'CLOSED';
      statusText = st;
      statusClass = st === 'OPEN' ? 'pos' : (['AFTER-HOURS', 'PRE-MARKET'].includes(st) ? 'cyan' : 'neu');
    }

    symbolBadge.innerHTML = `${ticker} ${sector} <span class="${statusClass}" style="margin-left: 6px; font-weight: bold; font-size: 11px;">[${statusText}]</span>`;
  }

  updateHeaderSpread(ob) {
    const spreadEl = document.getElementById('headerSpread');
    if (!spreadEl || !ob || !ob.bids || !ob.asks || !ob.bids.length || !ob.asks.length) return;
    const bid = Number(ob.bids[0].price);
    const ask = Number(ob.asks[0].price);
    let decimals = 2;
    if (bid < 0.01) decimals = 6;
    else if (bid < 0.5) decimals = 5;
    else if (bid < 2) decimals = 4;
    else if (bid < 20 && Math.abs(bid - Math.round(bid * 100) / 100) > 0.0001) decimals = 3;
    const bestBid = bid.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    const bestAsk = ask.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    spreadEl.innerText = `${bestBid} / ${bestAsk}`;
  }

  async loadHistoricalData(ticker, interval = null) {
    try {
      const activeInterval = interval || (this.priceChart ? this.priceChart.interval : '1M');
      const res = await fetch(`/api/ticks/${ticker}?interval=${activeInterval}`);
      if (res.ok) {
        const data = await res.json();
        if (this.priceChart && data.candles && this.currentTicker === ticker) {
          this.priceChart.setData(ticker, data.candles, null, activeInterval);
          if (data.candles.length > 0) {
            const last = data.candles[data.candles.length - 1];
            this.updateHeaderPrice(last.close, last.close >= last.open ? 'buy' : 'sell');
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

    const trimmed = rawCommand.trim();
    if (trimmed) {
      if (this.cmdHistory.length === 0 || this.cmdHistory[this.cmdHistory.length - 1] !== trimmed) {
        this.cmdHistory.push(trimmed);
      }
      this.historyIdx = -1;
    }

    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: trimmed })
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
        this.updateActiveSecurityBadge();

        if (resp.data && resp.data.candles && resp.data.candles.length > 0) {
          const curInt = this.priceChart ? this.priceChart.interval : '1M';
          if (this.priceChart && (!curInt || curInt === '1M')) {
            this.priceChart.setData(this.currentTicker, resp.data.candles, null, '1M');
          }
          const lastCandle = resp.data.candles[resp.data.candles.length - 1];
          this.updateHeaderPrice(lastCandle.close, lastCandle.close >= lastCandle.open ? 'buy' : 'sell');
        }

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

  fmtNum(val, dec = 2, fallback = 'N/A') {
    if (val === null || val === undefined || val === '' || isNaN(Number(val))) return fallback;
    return Number(val).toFixed(dec);
  }

  fmtCur(val, dec = 2, fallback = 'N/A') {
    if (val === null || val === undefined || val === '' || isNaN(Number(val))) return fallback;
    const n = Number(val);
    const sign = n < 0 ? '-' : '';
    return `${sign}$${Math.abs(n).toFixed(dec)}`;
  }

  fmtPct(val, dec = 2, showSign = true, fallback = 'N/A') {
    if (val === null || val === undefined || val === '' || isNaN(Number(val))) return fallback;
    const n = Number(val);
    const sign = (showSign && n > 0) ? '+' : '';
    return `${sign}${n.toFixed(dec)}%`;
  }

  showErrorModal(badgeText, title, message) {
    const modal = document.getElementById('terminalModal');
    const heading = document.getElementById('modalHeading');
    const badge = document.getElementById('modalBadge');
    const body = document.getElementById('modalBody');
    if (!modal || !heading || !badge || !body) return;
    badge.innerText = badgeText || 'ERR';
    heading.innerText = `${this.currentTicker} - ${title || 'DATA FEED ADVISORY'}`;
    body.innerHTML = `
      <div style="padding: 24px; text-align: center; border: 1px solid #ff3344; background: #1a0a0a; margin: 15px 0;">
        <div style="color: #ff3344; font-size: 14px; font-weight: bold; margin-bottom: 8px;">DATA FEED ADVISORY</div>
        <div style="color: #fff; font-size: 12px; margin-bottom: 12px;">${message || 'Upstream provider did not return valid data for this security.'}</div>
        <div style="font-size: 11px; color: var(--amber-dim);">TICKER: ${this.currentTicker} | FUNCTION: ${badgeText || 'N/A'}</div>
      </div>
      <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
        PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
      </div>
    `;
    modal.classList.remove('hidden');
  }

  async executeFunction(fn, data = null) {
    try {
      if (fn === 'DES') {
        if (!data) {
          const res = await fetch(`/api/des/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showDesModal(data);
      } else if (fn === 'ANR') {
        if (!data) {
          const res = await fetch(`/api/anr/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showAnrModal(data);
      } else if (fn === 'FA') {
        if (!data) {
          const res = await fetch(`/api/fa/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showFaModal(data);
      } else if (fn === 'RV') {
        if (!data) {
          const res = await fetch(`/api/rv/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showRvModal(data);
      } else if (fn === 'EE') {
        if (!data) {
          const res = await fetch(`/api/ee/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showEeModal(data);
      } else if (fn === 'WIRP') {
        if (!data) {
          const res = await fetch('/api/wirp');
          data = res.ok ? await res.json() : null;
        }
        this.showWirpModal(data);
      } else if (fn === 'WCRS') {
        if (!data) {
          const res = await fetch('/api/wcrs');
          data = res.ok ? await res.json() : null;
        }
        this.showWcrsModal(data);
      } else if (fn === 'FDM') {
        if (!data) {
          const res = await fetch('/api/fdm');
          data = res.ok ? await res.json() : null;
        }
        this.showFdmModal(data);
      } else if (fn === 'OMON') {
        if (!data) {
          const res = await fetch(`/api/options/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showOmonModal(data);
      } else if (fn === 'MAPS') {
        if (!data) {
          const res = await fetch('/api/heatmap');
          data = res.ok ? await res.json() : null;
        }
        this.showMapsModal(data);
      } else if (fn === 'AI') {
        if (!data) {
          const res = await fetch(`/api/research/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showAiModal(data);
      } else if (fn === 'INSD') {
        if (!data) {
          const res = await fetch(`/api/insiders/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showInsdModal(data);
      } else if (fn === 'HDS') {
        if (!data) {
          const res = await fetch(`/api/holders/${this.currentTicker}`);
          data = res.ok ? await res.json() : null;
        }
        this.showHdsModal(data);
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
    } catch (err) {
      console.error(`Error executing ${fn}:`, err);
      this.showErrorModal(fn, 'COMMUNICATION ERROR', err.message || 'Failed to retrieve command data');
    }
  }

  showDesModal(des) {
    if (!des) {
      this.showErrorModal('DES', 'SECURITY DESCRIPTION', 'No security description data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'DES';
      heading.innerText = `${des.symbol || this.currentTicker} ${des.sector || 'EQUITY'} // SECURITY DESCRIPTION & FUNDAMENTALS`;

      const numPrice = Number(des.price || 0);
      const numChg = Number(des.change || 0);
      const numPct = Number(des.change_pct || 0);
      const isPos = numChg >= 0;
      const chgClass = isPos ? 'pos' : 'neg';

      body.innerHTML = `
        <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid var(--border-amber); padding-bottom: 6px;">
          <div>
            <span style="font-size: 16px; font-weight: bold; color: var(--amber-bright);">${des.name || des.symbol || this.currentTicker}</span>
            <span class="neu" style="margin-left: 8px;">[${des.exchange || 'US'} | ${des.industry || 'General'}]</span>
          </div>
          <div>
            <span style="font-size: 16px; font-weight: bold; color: #fff;">${this.fmtNum(numPrice, 2)} USD</span>
            <span class="${chgClass}" style="margin-left: 6px; font-weight: bold;">${this.fmtCur(numChg, 2)} (${this.fmtPct(numPct, 2)})</span>
          </div>
        </div>

        <div class="des-grid">
          <div class="des-card">
            <div class="des-card-title">VALUATION &amp; CAPITAL STRUCTURE</div>
            <div class="des-row"><span class="des-label">MARKET CAP</span><span class="des-val">${des.market_cap || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">SHARES OUT</span><span class="des-val">${des.shares_out || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">P/E (TTM)</span><span class="des-val">${des.pe || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">FORWARD P/E</span><span class="des-val">${des.fwd_pe || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">DILUTED EPS</span><span class="des-val">${des.eps || 'N/A'}</span></div>
          </div>

          <div class="des-card">
            <div class="des-card-title">PRICE PERFORMANCE &amp; RISK</div>
            <div class="des-row"><span class="des-label">52-WEEK RANGE</span><span class="des-val">${des.range_52w || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">BETA (5Y MONTHLY)</span><span class="des-val">${des.beta || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">DIVIDEND YIELD</span><span class="des-val">${des.dividend_yield || des.div_yield || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">EX-DIVIDEND DATE</span><span class="des-val">${des.ex_div_date || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">CURRENCY</span><span class="des-val">${des.currency || 'USD'}</span></div>
          </div>

          <div class="des-card">
            <div class="des-card-title">FINANCIAL PROFILE (TTM)</div>
            <div class="des-row"><span class="des-label">REVENUE</span><span class="des-val">${des.revenue || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">NET INCOME</span><span class="des-val">${des.net_income || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">PRIMARY EXCHANGE</span><span class="des-val">${des.exchange || 'US'}</span></div>
          </div>

          <div class="des-card">
            <div class="des-card-title">CORPORATE GOVERNANCE</div>
            <div class="des-row"><span class="des-label">EXECUTIVE LEADERSHIP</span><span class="des-val">${des.ceo || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">GLOBAL HEADQUARTERS</span><span class="des-val">${des.hq || 'N/A'}</span></div>
            <div class="des-row"><span class="des-label">SECTOR CLASSIFICATION</span><span class="des-val">${des.sector || 'EQUITY'}</span></div>
          </div>
        </div>
        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering DES modal:', err);
      this.showErrorModal('DES', 'SECURITY DESCRIPTION ERROR', err.message);
    }
  }

  showAnrModal(anr) {
    if (!anr) {
      this.showErrorModal('ANR', 'ANALYST RECOMMENDATIONS', 'No analyst recommendation data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'ANR';
      heading.innerText = `${anr.symbol || this.currentTicker} - ANALYST RECOMMENDATIONS & TARGETS`;

      let brokersHtml = '';
      (anr.brokers || []).forEach(b => {
        const rating = b.rating || 'HOLD';
        const ratingCls = rating.includes('BUY') || rating.includes('OVERWEIGHT') ? 'pos' : (rating.includes('UNDER') || rating.includes('SELL') ? 'neg' : 'neu');
        brokersHtml += `
          <tr>
            <td><strong>${b.firm || 'Wall Street'}</strong></td>
            <td>${b.analyst || 'Analyst'}</td>
            <td class="${ratingCls}"><strong>${rating}</strong></td>
            <td class="text-right"><strong>${this.fmtCur(b.target, 2)}</strong></td>
            <td class="text-right neu">${b.date || '2026'}</td>
          </tr>
        `;
      });

      const upside = Number(anr.upside_pct || 0);
      const upsideCls = upside >= 0 ? 'pos' : 'neg';

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 15px; background: #141414; padding: 10px; border: 1px solid #282828;">
          <div style="flex: 1;">
            <div style="font-size: 11px; color: var(--text-muted);">CONSENSUS RATING</div>
            <div style="font-size: 16px; font-weight: bold; color: var(--amber-bright);">${anr.consensus || 'HOLD'} (${this.fmtNum(anr.consensus_score, 1)} / 5.0)</div>
            <div style="font-size: 11px; margin-top: 4px;">
              <span class="pos">${anr.buys || 0} BUYS</span> &bull; 
              <span class="neu">${anr.holds || 0} HOLDS</span> &bull; 
              <span class="neg">${anr.sells || 0} SELLS</span> (${anr.total_analysts || 0} TOTAL)
            </div>
          </div>
          <div style="flex: 1; border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">12M PRICE TARGET</div>
            <div style="font-size: 16px; font-weight: bold; color: #fff;">${this.fmtCur(anr.target_price, 2)} <span class="${upsideCls}" style="font-size: 13px;">(${this.fmtPct(upside, 2)})</span></div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
              RANGE: ${this.fmtCur(anr.target_low, 2)} - ${this.fmtCur(anr.target_high, 2)}
            </div>
          </div>
        </div>

        <div style="margin-bottom: 8px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">WALL STREET BROKER COVERAGE</div>
        <table class="modal-table">
          <thead>
            <tr>
              <th>BROKER FIRM</th>
              <th>LEAD ANALYST</th>
              <th>RECOMMENDATION</th>
              <th class="text-right">PRICE TARGET</th>
              <th class="text-right">DATE</th>
            </tr>
          </thead>
          <tbody>${brokersHtml || '<tr><td colspan="5" class="neu text-center">No active broker coverage found</td></tr>'}</tbody>
        </table>
        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering ANR modal:', err);
      this.showErrorModal('ANR', 'ANALYST RECOMMENDATIONS ERROR', err.message);
    }
  }

  showFaModal(fa) {
    if (!fa) {
      this.showErrorModal('FA', 'FINANCIAL ANALYSIS', 'No financial analysis data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'FA';
      heading.innerText = `${fa.symbol || this.currentTicker} - FINANCIAL ANALYSIS (5-YEAR HISTORICAL)`;

      const years = fa.years || fa.periods || ['2021', '2022', '2023', '2024', '2025'];
      const yearsHead = years.map(y => `<th class="text-right">${y}</th>`).join('');

      const renderRows = (items) => {
        if (!items) return '';
        let list = [];
        if (Array.isArray(items)) {
          list = items;
        } else if (typeof items === 'object') {
          list = Object.entries(items).map(([metric, vals]) => ({
            metric,
            vals: Array.isArray(vals) ? vals : [vals]
          }));
        }
        return list.map(item => `
          <tr>
            <td>${item.metric || 'Metric'}</td>
            ${(item.vals || []).map(v => `<td class="text-right"><strong>${v != null ? v : 'N/A'}</strong></td>`).join('')}
          </tr>
        `).join('');
      };

      body.innerHTML = `
        <div style="margin-bottom: 6px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">INCOME STATEMENT</div>
        <table class="modal-table" style="margin-bottom: 12px;">
          <thead><tr><th>METRIC (USD)</th>${yearsHead}</tr></thead>
          <tbody>${renderRows(fa.income_statement) || '<tr><td colspan="6" class="neu text-center">No income statement data</td></tr>'}</tbody>
        </table>

        <div style="margin-bottom: 6px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">BALANCE SHEET &amp; LIQUIDITY</div>
        <table class="modal-table" style="margin-bottom: 12px;">
          <thead><tr><th>METRIC (USD)</th>${yearsHead}</tr></thead>
          <tbody>${renderRows(fa.balance_sheet) || '<tr><td colspan="6" class="neu text-center">No balance sheet data</td></tr>'}</tbody>
        </table>

        <div style="margin-bottom: 6px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">CASH FLOW STATEMENT</div>
        <table class="modal-table">
          <thead><tr><th>METRIC (USD)</th>${yearsHead}</tr></thead>
          <tbody>${renderRows(fa.cash_flow) || '<tr><td colspan="6" class="neu text-center">No cash flow data</td></tr>'}</tbody>
        </table>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering FA modal:', err);
      this.showErrorModal('FA', 'FINANCIAL ANALYSIS ERROR', err.message);
    }
  }

  showRvModal(rv) {
    if (!rv) {
      this.showErrorModal('RV', 'RELATIVE VALUATION', 'No peer valuation data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'RV';
      heading.innerText = `${rv.symbol || this.currentTicker} - RELATIVE VALUATION & PEER COMP MATRIX`;

      let rowsHtml = '';
      (rv.peers || []).forEach(p => {
        const isTarget = p.symbol === (rv.symbol || this.currentTicker);
        rowsHtml += `
          <tr style="${isTarget ? 'background: #221800; font-weight: bold;' : ''}">
            <td><strong style="color: ${isTarget ? 'var(--amber-bright)' : '#fff'};">${p.symbol || 'N/A'}</strong></td>
            <td>${p.name || 'Peer'}</td>
            <td class="text-right">${this.fmtCur(p.price, 2)}</td>
            <td class="text-right">${p.pe != null ? p.pe : 'N/A'}</td>
            <td class="text-right">${p.fwd_pe != null ? p.fwd_pe : 'N/A'}</td>
            <td class="text-right">${p.ev_ebitda != null ? p.ev_ebitda : 'N/A'}</td>
            <td class="text-right">${p.ps != null ? p.ps : 'N/A'}</td>
            <td class="text-right">${p.op_margin != null ? p.op_margin : 'N/A'}</td>
            <td class="text-right">${p.roe != null ? p.roe : 'N/A'}</td>
            <td class="text-right">${p.div_yield != null ? p.div_yield : 'N/A'}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <div style="margin-bottom: 8px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">
          GICS INDUSTRY PEER COMPARISON MATRIX [${rv.industry || 'General'}]
        </div>
        <table class="modal-table">
          <thead>
            <tr>
              <th>TICKER</th>
              <th>COMPANY NAME</th>
              <th class="text-right">PRICE</th>
              <th class="text-right">P/E</th>
              <th class="text-right">FWD P/E</th>
              <th class="text-right">EV/EBITDA</th>
              <th class="text-right">P/S</th>
              <th class="text-right">OP MARGIN</th>
              <th class="text-right">ROE</th>
              <th class="text-right">DIV YIELD</th>
            </tr>
          </thead>
          <tbody>${rowsHtml || '<tr><td colspan="10" class="neu text-center">No peers available</td></tr>'}</tbody>
        </table>
        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering RV modal:', err);
      this.showErrorModal('RV', 'RELATIVE VALUATION ERROR', err.message);
    }
  }

  showEeModal(ee) {
    if (!ee) {
      this.showErrorModal('EE', 'EARNINGS ESTIMATES', 'No earnings estimate data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'EE';
      const isCrypto = ee.asset_type === 'DIGITAL_ASSET';
      heading.innerText = `${ee.symbol || this.currentTicker} - ${isCrypto ? 'PROTOCOL REVENUE & NETWORK METRICS' : 'EARNINGS ESTIMATES & SURPRISES'}`;

      let histHtml = '';
      const quarterly = ee.quarterly_history || [];
      if (quarterly.length === 0) {
        histHtml = '<tr><td colspan="6" class="text-center neu" style="padding: 12px;">NO QUARTERLY SURPRISE HISTORY AVAILABLE</td></tr>';
      } else {
        quarterly.forEach(q => {
          const surp = q.surprise_pct != null ? Number(q.surprise_pct) : 0;
          const cls = surp >= 0 ? 'pos' : 'neg';
          const repEps = q.reported_eps != null ? this.fmtCur(q.reported_eps, 2) : 'N/A';
          const conEps = q.consensus_eps != null ? this.fmtCur(q.consensus_eps, 2) : 'N/A';
          const surpStr = q.surprise_pct != null ? this.fmtPct(surp, 2) : (q.guidance || 'N/A');
          const revStr = q.revenue_reported ? (String(q.revenue_reported).startsWith('$') ? q.revenue_reported : `$${q.revenue_reported}`) : 'N/A';

          let revSurpStr = 'N/A';
          let revCls = 'neu';
          if (q.rev_surprise_pct != null) {
            const revSurp = Number(q.rev_surprise_pct);
            revCls = revSurp >= 0 ? 'pos' : 'neg';
            revSurpStr = this.fmtPct(revSurp, 2);
          } else if (q.guidance) {
            revCls = q.guidance === 'BEAT' ? 'pos' : (q.guidance === 'MISS' ? 'neg' : 'neu');
            revSurpStr = q.guidance;
          }

          histHtml += `
            <tr>
              <td><strong>${q.quarter || 'N/A'}</strong></td>
              <td class="text-right">${repEps}</td>
              <td class="text-right neu">${conEps}</td>
              <td class="text-right ${cls}"><strong>${surpStr}</strong></td>
              <td class="text-right">${revStr}</td>
              <td class="text-right ${revCls}">${revSurpStr}</td>
            </tr>
          `;
        });
      }

      let fwdHtml = '';
      const forward = ee.forward_estimates || [];
      if (forward.length === 0) {
        fwdHtml = '<tr><td colspan="5" class="text-center neu" style="padding: 12px;">NO FORWARD CONSENSUS GUIDANCE AVAILABLE</td></tr>';
      } else {
        forward.forEach(f => {
          const conEps = f.consensus_eps != null ? this.fmtCur(f.consensus_eps, 2) : 'N/A';
          const lowEps = f.low_eps != null ? this.fmtCur(f.low_eps, 2) : 'N/A';
          const highEps = f.high_eps != null ? this.fmtCur(f.high_eps, 2) : 'N/A';
          const estRev = f.est_revenue ? (String(f.est_revenue).startsWith('$') ? f.est_revenue : `$${f.est_revenue}`) : 'N/A';

          fwdHtml += `
            <tr>
              <td><strong>${f.quarter || 'N/A'}</strong></td>
              <td class="text-right" style="color: var(--amber-bright); font-weight: bold;">${conEps}</td>
              <td class="text-right neu">${lowEps}</td>
              <td class="text-right neu">${highEps}</td>
              <td class="text-right">${estRev}</td>
            </tr>
          `;
        });
      }

      body.innerHTML = `
        <div style="margin-bottom: 6px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">QUARTERLY EPS &amp; REVENUE SURPRISES</div>
        <table class="modal-table" style="margin-bottom: 14px;">
          <thead>
            <tr>
              <th>QUARTER</th>
              <th class="text-right">REPORTED EPS</th>
              <th class="text-right">CONSENSUS</th>
              <th class="text-right">EPS SURPRISE</th>
              <th class="text-right">REVENUE</th>
              <th class="text-right">REV SURPRISE</th>
            </tr>
          </thead>
          <tbody>${histHtml}</tbody>
        </table>

        <div style="margin-bottom: 6px; color: var(--amber-bright); font-weight: bold; font-size: 11px;">FORWARD CONSENSUS GUIDANCE</div>
        <table class="modal-table">
          <thead>
            <tr>
              <th>QUARTER</th>
              <th class="text-right">CONSENSUS EPS</th>
              <th class="text-right">LOW ESTIMATE</th>
              <th class="text-right">HIGH ESTIMATE</th>
              <th class="text-right">EST. REVENUE</th>
            </tr>
          </thead>
          <tbody>${fwdHtml}</tbody>
        </table>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering EE modal:', err);
      this.showErrorModal('EE', 'EARNINGS ESTIMATES ERROR', err.message);
    }
  }

  showWirpModal(wirp) {
    if (!wirp) {
      this.showErrorModal('WIRP', 'INTEREST RATE PROBABILITIES', 'No rate probability data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'WIRP';
      heading.innerText = 'WORLD INTEREST RATE PROBABILITIES - FOMC RATE MONITOR';

      let meetHtml = '';
      (wirp.meetings || []).forEach(m => {
        meetHtml += `
          <tr>
            <td><strong>${m.date || m.meeting_date || 'N/A'}</strong></td>
            <td class="text-right">${m.days_forward != null ? `${m.days_forward}d` : '--'}</td>
            <td class="text-right" style="color: var(--amber-bright); font-weight: bold;">${m.implied_rate || 'N/A'}</td>
            <td class="text-right pos">${this.fmtPct(m.prob_cut_25bp != null ? m.prob_cut_25bp : m.cut_prob_pct, 1, false)}</td>
            <td class="text-right pos">${this.fmtPct(m.prob_cut_50bp != null ? m.prob_cut_50bp : 0, 1, false)}</td>
            <td class="text-right neu">${this.fmtPct(m.prob_hold != null ? m.prob_hold : m.hold_prob_pct, 1, false)}</td>
            <td class="text-right" style="color: #00e5ff;">${m.bias || 'NEUTRAL'}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 15px; background: #141414; padding: 10px; border: 1px solid #282828;">
          <div>
            <div style="font-size: 11px; color: var(--text-muted);">CURRENT TARGET RATE</div>
            <div style="font-size: 16px; font-weight: bold; color: var(--amber-bright);">${wirp.current_target_rate || '4.75% - 5.00%'}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">EFFECTIVE FED FUNDS (EFFR)</div>
            <div style="font-size: 16px; font-weight: bold; color: #fff;">${wirp.effective_fed_funds_rate || '4.83%'}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">TERMINAL RATE PROJECTION</div>
            <div style="font-size: 16px; font-weight: bold; color: #00e5ff;">${wirp.terminal_rate || '3.50% - 3.75%'}</div>
          </div>
        </div>

        <table class="modal-table">
          <thead>
            <tr>
              <th>MEETING DATE</th>
              <th class="text-right">DAYS</th>
              <th class="text-right">IMPLIED RATE</th>
              <th class="text-right">% 25BP CUT</th>
              <th class="text-right">% 50BP CUT</th>
              <th class="text-right">% HOLD</th>
              <th class="text-right">MARKET BIAS</th>
            </tr>
          </thead>
          <tbody>${meetHtml || '<tr><td colspan="7" class="neu text-center">No FOMC meetings data available</td></tr>'}</tbody>
        </table>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering WIRP modal:', err);
      this.showErrorModal('WIRP', 'RATE PROBABILITIES ERROR', err.message);
    }
  }

  showWcrsModal(wcrs) {
    if (!wcrs) {
      this.showErrorModal('WCRS', 'WORLD CURRENCY RANKER', 'No currency data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'WCRS';
      heading.innerText = 'WORLD CURRENCY RANKER - GLOBAL FX PERFORMANCE VS USD';

      const currencies = wcrs.currencies || (Array.isArray(wcrs) ? wcrs : []);
      let rowsHtml = '';
      currencies.forEach((c, idx) => {
        const numChg = Number(c.change || 0);
        const numPct = Number(c.change_pct || 0);
        const cls = numPct >= 0 ? 'pos' : 'neg';
        rowsHtml += `
          <tr>
            <td><strong>#${idx + 1}</strong></td>
            <td><strong style="color: var(--amber-bright);">${c.pair || c.code || 'FX'}</strong></td>
            <td>${c.name || 'Currency'}</td>
            <td class="text-right"><strong>${this.fmtNum(c.spot, 4)}</strong></td>
            <td class="text-right ${cls}">${this.fmtNum(numChg, 4)}</td>
            <td class="text-right ${cls}"><strong>${this.fmtPct(numPct, 2)}</strong></td>
            <td class="text-right neu">${c.range_52w || 'N/A'}</td>
            <td class="text-right" style="color: #00e5ff;">${c.bias || 'NEUTRAL'}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <table class="modal-table">
          <thead>
            <tr>
              <th>RANK</th>
              <th>CURRENCY</th>
              <th>NAME</th>
              <th class="text-right">SPOT RATE</th>
              <th class="text-right">NET CHANGE</th>
              <th class="text-right">% CHANGE</th>
              <th class="text-right">52-WEEK RANGE</th>
              <th class="text-right">MARKET BIAS</th>
            </tr>
          </thead>
          <tbody>${rowsHtml || '<tr><td colspan="8" class="neu text-center">No FX rates available</td></tr>'}</tbody>
        </table>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering WCRS modal:', err);
      this.showErrorModal('WCRS', 'CURRENCY RANKER ERROR', err.message);
    }
  }

  showFdmModal(fdm) {
    if (!fdm) {
      this.showErrorModal('FDM', 'COMMODITIES & FUTURES', 'No commodities data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'FDM';
      heading.innerText = 'GLOBAL COMMODITIES & FUTURES MONITOR';

      const commodities = fdm.commodities || (Array.isArray(fdm) ? fdm : []);
      let rowsHtml = '';
      commodities.forEach(c => {
        const numChg = Number(c.change || 0);
        const numPct = Number(c.change_pct || 0);
        const cls = numPct >= 0 ? 'pos' : 'neg';
        rowsHtml += `
          <tr>
            <td><strong style="color: var(--amber-bright);">${c.symbol || c.commodity || 'CMD'}</strong></td>
            <td>${c.name || c.commodity || 'Commodity'}</td>
            <td><span class="badge" style="font-size: 9px;">${c.category || 'General'}</span></td>
            <td class="text-right"><strong>${this.fmtNum(c.price != null ? c.price : c.spot, 2)}</strong></td>
            <td class="text-right ${cls}">${this.fmtNum(numChg, 2)}</td>
            <td class="text-right ${cls}"><strong>${this.fmtPct(numPct, 2)}</strong></td>
            <td class="text-right neu">${c.unit || 'USD'}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <table class="modal-table">
          <thead>
            <tr>
              <th>SYMBOL</th>
              <th>COMMODITY CONTRACT</th>
              <th>CATEGORY</th>
              <th class="text-right">PRICE</th>
              <th class="text-right">CHANGE</th>
              <th class="text-right">% CHANGE</th>
              <th class="text-right">QUOTATION UNIT</th>
            </tr>
          </thead>
          <tbody>${rowsHtml || '<tr><td colspan="7" class="neu text-center">No commodities data available</td></tr>'}</tbody>
        </table>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering FDM modal:', err);
      this.showErrorModal('FDM', 'COMMODITIES ERROR', err.message);
    }
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
          <tr><td><strong>Up / Down</strong></td><td>Recall previous / next executed commands from history</td></tr>
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
    if (!ecoData) {
      this.showErrorModal('ECO', 'ECONOMIC CALENDAR', 'No economic calendar data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'ECO';
      heading.innerText = 'GLOBAL ECONOMIC CALENDAR & MACRO RELEASES';

      const events = ecoData.events || (Array.isArray(ecoData) ? ecoData : []);
      let rowsHtml = '';
      events.forEach(e => {
        const impact = (e.impact || 'MED').toUpperCase();
        const impClass = impact === 'HIGH' ? 'impact-high' : (impact === 'MED' ? 'impact-med' : 'impact-low');
        rowsHtml += `
          <tr>
            <td>${e.time || '--:--'}</td>
            <td><strong>${e.country || 'US'}</strong></td>
            <td>${e.indicator || e.event || 'Macro Event'}</td>
            <td>${e.period || 'Current'}</td>
            <td><strong>${e.actual != null ? e.actual : '--'}</strong></td>
            <td class="neu">${e.consensus != null ? e.consensus : (e.forecast != null ? e.forecast : '--')}</td>
            <td class="neu">${e.prior != null ? e.prior : '--'}</td>
            <td><span class="impact-badge ${impClass}">${impact}</span></td>
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
          <tbody>${rowsHtml || '<tr><td colspan="8" class="neu text-center">No economic events scheduled</td></tr>'}</tbody>
        </table>
        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering ECO modal:', err);
      this.showErrorModal('ECO', 'ECONOMIC CALENDAR ERROR', err.message);
    }
  }

  showOmonModal(omon) {
    if (!omon) {
      this.showErrorModal('OMON', 'OPTIONS MONITOR', 'No options chain data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'OMON';
      heading.innerText = `${omon.symbol || this.currentTicker} // OPTIONS MONITOR & BLACK-SCHOLES GREEKS`;

      let rowsHtml = '';
      (omon.chain || []).forEach(row => {
        const isAtm = row.is_atm;
        const isMaxPain = row.is_max_pain;
        const rowStyle = isAtm ? 'background: rgba(255, 176, 0, 0.12); font-weight: bold;' : (isMaxPain ? 'background: rgba(0, 240, 255, 0.1);' : '');
        const strikeBadge = isAtm ? ' <span style="color: var(--amber-bright); font-size: 9px;">[ATM]</span>' : (isMaxPain ? ' <span style="color: #00f0ff; font-size: 9px;">[MAX PAIN]</span>' : '');

        rowsHtml += `
          <tr style="${rowStyle}">
            <td class="text-right" style="color: #00f0ff;">${row.call_delta != null ? row.call_delta : 'N/A'}</td>
            <td class="text-right neu">${row.call_gamma != null ? row.call_gamma : 'N/A'}</td>
            <td class="text-right neu">${row.call_theta != null ? row.call_theta : 'N/A'}</td>
            <td class="text-right neu">${row.call_vega != null ? row.call_vega : 'N/A'}</td>
            <td class="text-right" style="color: #00ff66;">${this.fmtCur(row.call_bid, 2)}</td>
            <td class="text-right" style="color: #00ff66;">${this.fmtCur(row.call_ask, 2)}</td>
            <td class="text-right neu">${this.fmtPct(Number(row.call_iv || 0) * 100, 1, false)}</td>
            <td class="text-center" style="font-weight: bold; color: var(--amber-bright); background: #1c1c1c; border-left: 1px solid #333; border-right: 1px solid #333;">${this.fmtNum(row.strike, 2)}${strikeBadge}</td>
            <td class="text-right neu">${this.fmtPct(Number(row.put_iv || 0) * 100, 1, false)}</td>
            <td class="text-right" style="color: #ff3344;">${this.fmtCur(row.put_bid, 2)}</td>
            <td class="text-right" style="color: #ff3344;">${this.fmtCur(row.put_ask, 2)}</td>
            <td class="text-right neu">${row.put_vega != null ? row.put_vega : 'N/A'}</td>
            <td class="text-right neu">${row.put_theta != null ? row.put_theta : 'N/A'}</td>
            <td class="text-right neu">${row.put_gamma != null ? row.put_gamma : 'N/A'}</td>
            <td class="text-right" style="color: #00f0ff;">${row.put_delta != null ? row.put_delta : 'N/A'}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 15px; background: #141414; padding: 10px; border: 1px solid #282828;">
          <div>
            <div style="font-size: 11px; color: var(--text-muted);">UNDERLYING SPOT</div>
            <div style="font-size: 16px; font-weight: bold; color: var(--amber-bright);">${this.fmtCur(omon.spot_price, 2)}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">EXPIRATION (DTE)</div>
            <div style="font-size: 16px; font-weight: bold; color: #fff;">${omon.expiration || 'FRONT'} (${omon.dte || 0} DTE)</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">ATM VOLATILITY (IV)</div>
            <div style="font-size: 16px; font-weight: bold; color: #00e5ff;">${this.fmtPct(Number(omon.atm_iv || 0) * 100, 1, false)}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">MAX PAIN STRIKE</div>
            <div style="font-size: 16px; font-weight: bold; color: #ff00ea;">${this.fmtCur(omon.max_pain_strike, 2)}</div>
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table class="modal-table" style="font-size: 11px;">
            <thead>
              <tr>
                <th colspan="7" class="text-center" style="background: rgba(0, 255, 102, 0.1); color: #00ff66;">CALLS (BULLISH)</th>
                <th class="text-center" style="background: #252525; color: var(--amber-bright);">STRIKE</th>
                <th colspan="7" class="text-center" style="background: rgba(255, 51, 68, 0.1); color: #ff3344;">PUTS (BEARISH)</th>
              </tr>
              <tr>
                <th class="text-right">DELTA (Δ)</th>
                <th class="text-right">GAMMA (Γ)</th>
                <th class="text-right">THETA (Θ)</th>
                <th class="text-right">VEGA (ν)</th>
                <th class="text-right">BID</th>
                <th class="text-right">ASK</th>
                <th class="text-right">IV</th>
                <th class="text-center">STRIKE</th>
                <th class="text-right">IV</th>
                <th class="text-right">BID</th>
                <th class="text-right">ASK</th>
                <th class="text-right">VEGA (ν)</th>
                <th class="text-right">THETA (Θ)</th>
                <th class="text-right">GAMMA (Γ)</th>
                <th class="text-right">DELTA (Δ)</th>
              </tr>
            </thead>
            <tbody>${rowsHtml || '<tr><td colspan="15" class="neu text-center">No option chain available</td></tr>'}</tbody>
          </table>
        </div>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          BLACK-SCHOLES CONTINUOUS FORMULATION // RISK-FREE RATE: 4.50% // PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO CLOSE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering OMON modal:', err);
      this.showErrorModal('OMON', 'OPTIONS MONITOR ERROR', err.message);
    }
  }

  showMapsModal(mapData) {
    if (!mapData) {
      this.showErrorModal('MAPS', 'MARKET HEATMAP', 'No market heatmap data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'MAPS';
      heading.innerText = `S&P 500 MARKET HEATMAP // GICS SECTOR TREEMAP (${mapData.index || 'SPX'})`;

      let sectorsHtml = '';
      (mapData.sectors || []).forEach(sec => {
        let tickersHtml = '';
        (sec.constituents || []).forEach(stock => {
          const numPct = Number(stock.change_pct || 0);
          const isPos = numPct >= 0;
          const bg = isPos ? (numPct > 2 ? 'rgba(0, 200, 80, 0.45)' : 'rgba(0, 160, 60, 0.3)') : (numPct < -2 ? 'rgba(220, 40, 50, 0.45)' : 'rgba(180, 40, 50, 0.3)');
          const border = isPos ? '#00aa44' : '#cc2233';

          tickersHtml += `
            <div class="treemap-card" data-symbol="${stock.symbol}" style="background: ${bg}; border: 1px solid ${border}; border-radius: 2px; padding: 6px 8px; cursor: pointer; flex: 1 1 90px; min-width: 80px; text-align: center; transition: transform 0.1s, box-shadow 0.1s;">
              <div style="font-weight: bold; font-size: 13px; color: #fff;">${stock.symbol}</div>
              <div style="font-size: 11px; font-weight: bold; color: ${isPos ? '#00ff66' : '#ff5566'};">${this.fmtPct(numPct, 2)}</div>
              <div style="font-size: 9px; color: rgba(255,255,255,0.7);">${this.fmtCur(stock.price, 2)}</div>
              <div style="font-size: 8px; color: #aaa;">$${stock.mkt_cap_b != null ? stock.mkt_cap_b : '--'}B</div>
            </div>
          `;
        });

        sectorsHtml += `
          <div style="background: #111; border: 1px solid #282828; padding: 10px; margin-bottom: 12px; border-radius: 3px;">
            <div style="font-size: 11px; font-weight: bold; color: var(--amber-bright); margin-bottom: 8px; text-transform: uppercase; border-bottom: 1px solid #222; padding-bottom: 4px;">
              ${sec.sector || 'Sector'} (${(sec.constituents || []).length} STOCKS)
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              ${tickersHtml}
            </div>
          </div>
        `;
      });

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 12px; background: #141414; padding: 10px; border: 1px solid #282828;">
          <div>
            <div style="font-size: 11px; color: var(--text-muted);">MARKET PERFORMANCE</div>
            <div style="font-size: 15px; font-weight: bold; color: #fff;">${mapData.total_symbols || 0} KEY CONSTITUENTS</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">ADVANCERS</div>
            <div style="font-size: 15px; font-weight: bold; color: #00ff66;">${mapData.advancers || 0} TICKERS</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">DECLINERS</div>
            <div style="font-size: 15px; font-weight: bold; color: #ff3344;">${mapData.decliners || 0} TICKERS</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">ACTION</div>
            <div style="font-size: 11px; color: var(--amber-bright); margin-top: 2px;">CLICK ANY TILE TO LOAD WORKSTATION CHART &amp; DEPTH</div>
          </div>
        </div>

        <div style="max-height: 520px; overflow-y: auto; padding-right: 4px;">
          ${sectorsHtml || '<div class="neu text-center">No market sector data available</div>'}
        </div>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 10px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;

      // Wire clicks on treemap tiles to load ticker
      body.querySelectorAll('.treemap-card').forEach(tile => {
        tile.addEventListener('click', () => {
          const sym = tile.dataset.symbol;
          if (sym) {
            this.closeModal();
            this.executeCommand(`${sym} GP <GO>`);
          }
        });
      });

      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering MAPS modal:', err);
      this.showErrorModal('MAPS', 'HEATMAP ERROR', err.message);
    }
  }

  showAiModal(ai) {
    if (!ai) {
      this.showErrorModal('AI', 'AI RESEARCH', 'No research memo returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'AI';
      heading.innerText = `${ai.symbol || this.currentTicker} // AUTONOMOUS EQUITY RESEARCH ANALYST MEMO`;

      let moatsHtml = '';
      (ai.competitive_moat || []).forEach(m => {
        const parts = String(m).split(':');
        moatsHtml += `<li style="margin-bottom: 6px; color: #ddd;"><strong style="color: #00f0ff;">${parts[0]}:</strong>${parts.slice(1).join(':')}</li>`;
      });

      let catHtml = '';
      (ai.growth_catalysts || []).forEach(c => {
        const parts = String(c).split(':');
        catHtml += `<li style="margin-bottom: 6px; color: #ddd;"><strong style="color: #00ff66;">${parts[0]}:</strong>${parts.slice(1).join(':')}</li>`;
      });

      let riskHtml = '';
      (ai.downside_risks || []).forEach(r => {
        const parts = String(r).split(':');
        riskHtml += `<li style="margin-bottom: 6px; color: #ddd;"><strong style="color: #ff3344;">${parts[0]}:</strong>${parts.slice(1).join(':')}</li>`;
      });

      const rating = ai.rating || 'NEUTRAL';
      const isBuy = rating.includes('BUY') || rating.includes('OUTPERFORM');
      const ratingColor = isBuy ? '#00ff66' : '#ffb000';
      const val = ai.valuation_assessment || {};

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 15px; background: #141414; padding: 12px; border: 1px solid #282828;">
          <div>
            <div style="font-size: 11px; color: var(--text-muted);">ANALYST RATING</div>
            <div style="font-size: 18px; font-weight: bold; color: ${ratingColor};">${rating}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">PRICE TARGET (12M)</div>
            <div style="font-size: 18px; font-weight: bold; color: var(--amber-bright);">${this.fmtCur(ai.target_price, 2)}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">IMPLIED UPSIDE</div>
            <div style="font-size: 18px; font-weight: bold; color: #00ff66;">${this.fmtPct(ai.upside_pct, 2)}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">SOURCE</div>
            <div style="font-size: 12px; color: #fff; margin-top: 3px;">${ai.analyst || 'Autonomous Research Engine'}</div>
          </div>
        </div>

        <div style="max-height: 480px; overflow-y: auto; padding-right: 6px; font-size: 12px; line-height: 1.5;">
          <div style="background: #111; border: 1px solid #252525; padding: 12px; margin-bottom: 12px; border-left: 3px solid var(--amber-bright);">
            <div style="font-weight: bold; color: var(--amber-bright); margin-bottom: 6px; font-size: 12px;">EXECUTIVE INVESTMENT THESIS</div>
            <div style="color: #eee;">${ai.investment_thesis || 'No investment thesis provided.'}</div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div style="background: #111; border: 1px solid #252525; padding: 12px; border-top: 2px solid #00f0ff;">
              <div style="font-weight: bold; color: #00f0ff; margin-bottom: 8px;">COMPETITIVE MOAT &amp; DEFENSIVE ADVANTAGES</div>
              <ul style="padding-left: 16px; margin: 0;">${moatsHtml || '<li>No moats identified</li>'}</ul>
            </div>
            <div style="background: #111; border: 1px solid #252525; padding: 12px; border-top: 2px solid #00ff66;">
              <div style="font-weight: bold; color: #00ff66; margin-bottom: 8px;">HIGH-CONVICTION GROWTH CATALYSTS</div>
              <ul style="padding-left: 16px; margin: 0;">${catHtml || '<li>No catalysts identified</li>'}</ul>
            </div>
          </div>

          <div style="background: #111; border: 1px solid #252525; padding: 12px; margin-bottom: 12px; border-top: 2px solid #ff3344;">
            <div style="font-weight: bold; color: #ff3344; margin-bottom: 8px;">DOWNSIDE SCENARIO &amp; KEY RISK FACTORS</div>
            <ul style="padding-left: 16px; margin: 0;">${riskHtml || '<li>No specific downside risks highlighted</li>'}</ul>
          </div>

          <div style="background: #111; border: 1px solid #252525; padding: 12px;">
            <div style="font-weight: bold; color: var(--amber-bright); margin-bottom: 8px;">VALUATION MULTIPLES &amp; MULTI-YEAR VERDICT</div>
            <div style="display: flex; gap: 15px; margin-bottom: 8px; flex-wrap: wrap;">
              <div><span style="color: #888;">FWD P/E:</span> <strong style="color: #fff;">${val.fwd_pe || 'N/A'}</strong></div>
              <div><span style="color: #888;">EV/EBITDA:</span> <strong style="color: #fff;">${val.ev_ebitda || 'N/A'}</strong></div>
              <div><span style="color: #888;">FCF YIELD:</span> <strong style="color: #00ff66;">${val.free_cash_flow_yield || 'N/A'}</strong></div>
              <div><span style="color: #888;">DIV YIELD:</span> <strong style="color: var(--amber-bright);">${val.dividend_yield || 'N/A'}</strong></div>
            </div>
            <div style="color: #ffcc00; font-weight: bold; border-top: 1px solid #222; padding-top: 6px;">
              VERDICT: ${val.verdict || 'Fairly valued'}
            </div>
          </div>
        </div>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 10px;">
          PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO RETURN TO WORKSPACE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering AI modal:', err);
      this.showErrorModal('AI', 'AI RESEARCH ERROR', err.message);
    }
  }

  showInsdModal(insd) {
    if (!insd) {
      this.showErrorModal('INSD', 'INSIDER TRANSACTIONS', 'No insider data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'INSD';
      heading.innerText = `${insd.symbol || this.currentTicker} // SEC FORM 4 INSIDER TRANSACTIONS`;

      const sentiment = insd.sentiment || 'NEUTRAL';
      const isBuySentiment = sentiment.includes('BUY');
      const sentColor = isBuySentiment ? '#00ff66' : '#ff3344';

      let rowsHtml = '';
      (insd.transactions || []).forEach(t => {
        const tType = t.type || 'Transaction';
        const isSale = tType.includes('Sale');
        const typeColor = isSale ? '#ff3344' : '#00ff66';
        const sharesNum = Number(t.shares || 0);
        rowsHtml += `
          <tr>
            <td>${t.date || '--'}</td>
            <td><strong style="color: #fff;">${t.name || 'Insider'}</strong></td>
            <td class="neu">${t.title || '--'}</td>
            <td style="color: ${typeColor}; font-weight: bold;">${tType}</td>
            <td class="text-right" style="color: ${typeColor};">${isSale ? '-' : '+'}${sharesNum.toLocaleString()}</td>
            <td class="text-right">${this.fmtCur(t.price, 2)}</td>
            <td class="text-right" style="font-weight: bold; color: ${typeColor};">${this.fmtCur(t.value, 0)}</td>
            <td class="text-right neu">${Number(t.shares_owned || 0).toLocaleString()}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 15px; background: #141414; padding: 10px; border: 1px solid #282828;">
          <div>
            <div style="font-size: 11px; color: var(--text-muted);">INSIDER SENTIMENT</div>
            <div style="font-size: 16px; font-weight: bold; color: ${sentColor};">${sentiment}</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">NET SHARES FLOW</div>
            <div style="font-size: 16px; font-weight: bold; color: ${sentColor};">${Number(insd.net_shares_flow || 0).toLocaleString()} SHARES</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">PERIOD</div>
            <div style="font-size: 16px; font-weight: bold; color: #fff;">${insd.period || 'LTM'}</div>
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table class="modal-table">
            <thead>
              <tr>
                <th>DATE</th>
                <th>INSIDER NAME</th>
                <th>CORPORATE TITLE</th>
                <th>TRANSACTION TYPE</th>
                <th class="text-right">SHARES</th>
                <th class="text-right">PRICE</th>
                <th class="text-right">NET VALUE</th>
                <th class="text-right">POST SHARES</th>
              </tr>
            </thead>
            <tbody>${rowsHtml || '<tr><td colspan="8" class="neu text-center">No recent insider filings</td></tr>'}</tbody>
          </table>
        </div>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          DATA SOURCE: US SEC EDGAR ELECTRONIC FORM 4 SYSTEM // PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO CLOSE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering INSD modal:', err);
      this.showErrorModal('INSD', 'INSIDER TRANSACTIONS ERROR', err.message);
    }
  }

  showHdsModal(hds) {
    if (!hds) {
      this.showErrorModal('HDS', 'OWNERSHIP BREAKDOWN', 'No institutional data returned.');
      return;
    }
    try {
      const modal = document.getElementById('terminalModal');
      const heading = document.getElementById('modalHeading');
      const badge = document.getElementById('modalBadge');
      const body = document.getElementById('modalBody');

      badge.innerText = 'HDS';
      heading.innerText = `${hds.symbol || this.currentTicker} // 13F INSTITUTIONAL OWNERSHIP BREAKDOWN`;

      let rowsHtml = '';
      (hds.holders || []).forEach(h => {
        const chgNum = Number(h.change_shares || 0);
        const isPos = chgNum >= 0;
        const chgColor = isPos ? '#00ff66' : '#ff3344';
        const sign = isPos ? '+' : '';
        rowsHtml += `
          <tr>
            <td class="text-center" style="color: var(--amber-bright); font-weight: bold;">${h.rank || '--'}</td>
            <td><strong style="color: #fff;">${h.name || 'Institutional Manager'}</strong></td>
            <td class="text-right">${Number(h.shares || 0).toLocaleString()}</td>
            <td class="text-right" style="color: var(--amber-bright); font-weight: bold;">$${this.fmtNum(h.value_b, 2)}B</td>
            <td class="text-right" style="color: #00f0ff; font-weight: bold;">${this.fmtPct(h.pct_float, 2, false)}</td>
            <td class="text-right" style="color: ${chgColor};">${sign}${chgNum.toLocaleString()}</td>
            <td class="text-right neu">${h.date || '--'}</td>
          </tr>
        `;
      });

      body.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 15px; background: #141414; padding: 10px; border: 1px solid #282828;">
          <div>
            <div style="font-size: 11px; color: var(--text-muted);">TOP INSTITUTIONAL CONCENTRATION</div>
            <div style="font-size: 16px; font-weight: bold; color: #00f0ff;">${this.fmtPct(hds.top_holders_ownership_pct, 1, false)} OF FLOAT</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">REPORTED HOLDERS</div>
            <div style="font-size: 16px; font-weight: bold; color: #fff;">TOP ${hds.top_holders_count || 0} ASSET MANAGERS</div>
          </div>
          <div style="border-left: 1px solid #282828; padding-left: 15px;">
            <div style="font-size: 11px; color: var(--text-muted);">REGULATORY FILING SOURCE</div>
            <div style="font-size: 14px; font-weight: bold; color: var(--amber-bright);">${hds.source || 'SEC EDGAR 13F'}</div>
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table class="modal-table">
            <thead>
              <tr>
                <th class="text-center">RANK</th>
                <th>INSTITUTIONAL MANAGER</th>
                <th class="text-right">SHARES HELD</th>
                <th class="text-right">MARKET VALUE ($B)</th>
                <th class="text-right">% FLOAT</th>
                <th class="text-right">Q/Q NET CHANGE</th>
                <th class="text-right">REPORT DATE</th>
              </tr>
            </thead>
            <tbody>${rowsHtml || '<tr><td colspan="7" class="neu text-center">No institutional filings available</td></tr>'}</tbody>
          </table>
        </div>

        <div style="text-align: right; font-size: 10px; color: var(--text-muted); margin-top: 12px;">
          DATA SOURCE: US SEC EDGAR FORM 13F-HR // PRESS &lt;ESC&gt; OR CLICK &lt;CNCL&gt; TO CLOSE
        </div>
      `;
      modal.classList.remove('hidden');
    } catch (err) {
      console.error('Error rendering HDS modal:', err);
      this.showErrorModal('HDS', 'OWNERSHIP ERROR', err.message);
    }
  }

  closeModal() {
    const modal = document.getElementById('terminalModal');
    if (modal) modal.classList.add('hidden');
    const modalFunctions = ['DES', 'HELP', 'ECO', 'ANR', 'FA', 'RV', 'EE', 'WIRP', 'WCRS', 'FDM', 'OMON', 'MAPS', 'AI', 'INSD', 'HDS'];
    if (modalFunctions.includes(this.currentFunction)) {
      this.setFunction('GP');
    }
  }

  updateHeaderPrice(price, side) {
    const priceEl = document.getElementById('livePrice');
    if (!priceEl || price === null || price === undefined || isNaN(price)) return;
    const numPrice = Number(price);
    let decimals = 2;
    if (numPrice < 0.01) decimals = 6;
    else if (numPrice < 0.5) decimals = 5;
    else if (numPrice < 2) decimals = 4;
    else if (numPrice < 20 && Math.abs(numPrice - Math.round(numPrice * 100) / 100) > 0.0001) decimals = 3;
    priceEl.innerText = numPrice.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
    priceEl.className = side === 'buy' ? 'tick-up' : 'tick-down';
    setTimeout(() => { priceEl.className = ''; }, 350);
  }

  renderWEI(indices) {
    const tbody = document.getElementById('weiBody');
    if (!tbody || !indices) return;
    let html = '';
    indices.forEach(idx => {
      const numChg = Number(idx.change || 0);
      const isPos = numChg >= 0;
      const cls = isPos ? 'pos' : 'neg';
      html += `
        <tr id="row-${idx.symbol}" data-symbol="${idx.symbol}">
          <td><strong>${idx.symbol}</strong></td>
          <td class="neu">${idx.name || idx.symbol}</td>
          <td class="text-right" id="price-${idx.symbol}">${this.fmtNum(idx.price, 2)}</td>
          <td class="text-right ${cls}" id="chg-${idx.symbol}">${this.fmtNum(numChg, 2)}</td>
          <td class="text-right ${cls}" id="pct-${idx.symbol}">${this.fmtPct(idx.change_pct, 2)}</td>
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
    (ticks || []).forEach(t => {
      const priceEl = document.getElementById(`price-${t.symbol}`);
      const chgEl = document.getElementById(`chg-${t.symbol}`);
      const pctEl = document.getElementById(`pct-${t.symbol}`);
      if (priceEl && chgEl && pctEl) {
        const numChg = Number(t.change || 0);
        const isPos = numChg >= 0;
        const cls = isPos ? 'pos' : 'neg';
        priceEl.innerText = this.fmtNum(t.price, 2);
        priceEl.className = `text-right ${isPos ? 'tick-up' : 'tick-down'}`;
        setTimeout(() => { priceEl.className = 'text-right'; }, 350);
        chgEl.className = `text-right ${cls}`;
        chgEl.innerText = this.fmtNum(numChg, 2);
        pctEl.className = `text-right ${cls}`;
        pctEl.innerText = this.fmtPct(t.change_pct, 2);
      }
    });
  }

  renderNews(newsItems) {
    const list = document.getElementById('newsList');
    if (!list || !newsItems) return;
    let html = '';
    newsItems.forEach(n => {
      const sentClass = n.sentiment === 'BULLISH' ? 'pos' : (n.sentiment === 'BEARISH' ? 'neg' : 'neu');
      html += `
        <div class="news-item" style="cursor: pointer;" data-ticker="${n.ticker}" title="Click to load ${n.ticker}">
          <div class="news-time">${n.time}</div>
          <div class="news-ticker">${n.ticker}</div>
          <div class="news-headline">${n.headline}</div>
          <div class="news-tag ${sentClass}">${n.source}</div>
        </div>
      `;
    });
    list.innerHTML = html;

    list.querySelectorAll('.news-item').forEach(el => {
      el.addEventListener('click', () => {
        const ticker = el.dataset.ticker;
        if (ticker && ticker !== 'MARKET' && ticker !== 'US10Y') {
          const sector = ticker.includes('USD') ? 'CRNCY' : 'EQUITY';
          this.executeCommand(`${ticker} ${sector} GP <GO>`);
        }
      });
    });
  }

  renderYieldCurve(curve) {
    const container = document.getElementById('yieldCurveData');
    if (!container || !curve) return;
    let html = `
      <div style="font-size: 11px; margin-bottom: 6px;">
        <span>2Y/10Y SPREAD: <strong class="${curve.inverted ? 'neg' : 'pos'}">${curve.spread_2_10_bps != null ? curve.spread_2_10_bps : 'N/A'} BPS</strong></span>
        ${curve.inverted ? '<span class="neg" style="margin-left: 8px;">[INVERTED]</span>' : ''}
      </div>
      <table class="terminal-table">
        <thead>
          <tr><th>TENOR</th><th class="text-right">YIELD</th><th class="text-right">CHG</th></tr>
        </thead>
        <tbody>
    `;
    (curve.tenors || []).forEach(t => {
      const numChg = Number(t.change || 0);
      const cls = numChg >= 0 ? 'pos' : 'neg';
      html += `
        <tr>
          <td>${t.tenor}</td>
          <td class="text-right"><strong>${this.fmtPct(t.yield, 2, false)}</strong></td>
          <td class="text-right ${cls}">${this.fmtNum(numChg, 2)}</td>
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
