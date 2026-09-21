/*
 * PD3board Professional TradingView Lightweight Charts Financial Engine
 * Features: High-performance 60 FPS WebGL/Canvas rendering, native crosshairs,
 * smooth multi-timeframe pan/zoom, interactive Bloomberg HUD, volume overlays,
 * and live-updating technical indicators (SMA 20, SMA 50, Bollinger Bands, RSI, MACD).
 */

class PriceChart {
  constructor(containerId) {
    let target = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
    if (!target) return;

    // If target is a canvas element, replace it with a div container
    if (target.tagName.toLowerCase() === 'canvas') {
      const parent = target.parentElement;
      const div = document.createElement('div');
      div.id = target.id;
      div.style.width = '100%';
      div.style.height = '100%';
      div.style.position = 'relative';
      parent.replaceChild(div, target);
      target = div;
    }

    this.container = target;
    this.container.style.position = 'relative';
    this.container.style.width = '100%';
    this.container.style.height = '100%';

    this.symbol = 'BTCUSDT';
    this.interval = '1M';
    this.currentPrice = 0;
    this.candles = [];
    this.rawCandles = [];
    this.timeZoneMode = 'EST';

    // Indicator states
    this.indicators = {
      SMA20: false,
      SMA50: false,
      BOLL: false,
      RSI: false,
      MACD: false
    };

    // Series references
    this.candleSeries = null;
    this.volumeSeries = null;
    this.sma20Series = null;
    this.sma50Series = null;
    this.bollUpperSeries = null;
    this.bollLowerSeries = null;
    this.bollMidSeries = null;
    this.rsiSeries = null;
    this.macdHistSeries = null;
    this.macdLineSeries = null;
    this.macdSignalSeries = null;

    // Create Bloomberg HUD overlay
    this.createHud();

    // Initialize TradingView Chart
    this.initChart();

    // Bind auto-resize
    if (typeof ResizeObserver !== 'undefined') {
      this.resizeObserver = new ResizeObserver(entries => {
        if (!entries || !entries.length || !this.chart) return;
        const { width, height } = entries[0].contentRect;
        if (width > 0 && height > 0) {
          this.chart.applyOptions({ width, height });
        }
      });
      this.resizeObserver.observe(this.container);
    }
  }

  setTimeZone(mode = 'EST') {
    this.timeZoneMode = mode === 'UTC' ? 'UTC' : 'EST';
    if (!this.chart) return;
    const tz = this.timeZoneMode === 'UTC' ? 'UTC' : 'America/New_York';
    const tzSuffix = this.timeZoneMode === 'UTC' ? ' UTC' : ' ET';

    this.chart.applyOptions({
      localization: {
        locale: 'en-US',
        dateFormat: 'yyyy-MM-dd',
        timeFormatter: (ts) => {
          if (!ts) return '';
          const d = typeof ts === 'number' ? new Date(ts * 1000) : new Date(ts.year, ts.month - 1, ts.day);
          return d.toLocaleTimeString('en-US', {
            timeZone: tz,
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
          }) + tzSuffix;
        },
      },
      timeScale: {
        tickMarkFormatter: (time, tickMarkType, locale) => {
          if (!time) return '';
          const d = typeof time === 'number' ? new Date(time * 1000) : new Date(time.year, time.month - 1, time.day);
          if (tickMarkType === 0) {
            return d.getFullYear().toString();
          } else if (tickMarkType === 1) {
            return d.toLocaleDateString('en-US', { timeZone: tz, month: 'short' });
          } else if (tickMarkType === 2) {
            return d.toLocaleDateString('en-US', { timeZone: tz, month: 'numeric', day: 'numeric' });
          } else {
            return d.toLocaleTimeString('en-US', {
              timeZone: tz,
              hour12: false,
              hour: '2-digit',
              minute: '2-digit'
            });
          }
        },
      }
    });
    this.updateHud(null);
  }

  createHud() {
    let hud = this.container.querySelector('.chart-hud');
    if (!hud) {
      hud = document.createElement('div');
      hud.className = 'chart-hud';
      this.container.appendChild(hud);
    }
    this.hudElement = hud;
    this.updateHud(null);
  }

  updateHud(bar) {
    if (!this.hudElement) return;
    const targetBar = bar || (this.candles.length ? this.candles[this.candles.length - 1] : null);

    if (!targetBar) {
      this.hudElement.innerHTML = `
        <span class="hud-symbol">${this.symbol} [${this.interval}]</span>
        <span>TIME: <span class="hud-val">--</span></span>
        <span>O: <span class="hud-val">--</span></span>
        <span>H: <span class="hud-val">--</span></span>
        <span>L: <span class="hud-val">--</span></span>
        <span>C: <span class="hud-val">--</span></span>
        <span>VOL: <span class="hud-val">--</span></span>
      `;
      return;
    }

    const tz = this.timeZoneMode === 'UTC' ? 'UTC' : 'America/New_York';
    const tzSuffix = this.timeZoneMode === 'UTC' ? ' UTC' : ' ET';
    let timeStr = '--';
    if (targetBar.time) {
      const d = typeof targetBar.time === 'number' ? new Date(targetBar.time * 1000) : new Date(targetBar.time.year, targetBar.time.month - 1, targetBar.time.day);
      timeStr = this.interval === '1D'
        ? d.toLocaleDateString('en-US', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' })
        : d.toLocaleTimeString('en-US', { timeZone: tz, hour12: false, hour: '2-digit', minute: '2-digit' }) + tzSuffix;
    }

    const open = Number(targetBar.open);
    const high = Number(targetBar.high);
    const low = Number(targetBar.low);
    const close = Number(targetBar.close);
    const vol = Number(targetBar.volume || 0);
    const chg = close - open;
    const chgPct = open > 0 ? (chg / open) * 100 : 0;
    const isUp = chg >= 0;
    const sign = isUp ? '+' : '';
    const chgClass = isUp ? 'hud-up' : 'hud-down';

    const fmt = (v) => {
      if (Math.abs(v) >= 1000) return v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      if (Math.abs(v) >= 1) return v.toFixed(2);
      if (Math.abs(v) >= 0.001) return v.toFixed(4);
      return v.toFixed(6);
    };

    const fmtVol = (v) => {
      if (v >= 1e9) return (v / 1e9).toFixed(2) + 'B';
      if (v >= 1e6) return (v / 1e6).toFixed(2) + 'M';
      if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
      return v.toFixed(0);
    };

    this.hudElement.innerHTML = `
      <span class="hud-symbol">${this.symbol} [${this.interval}]</span>
      <span>TIME: <span class="hud-val">${timeStr}</span></span>
      <span>O: <span class="hud-val">${fmt(open)}</span></span>
      <span>H: <span class="hud-val">${fmt(high)}</span></span>
      <span>L: <span class="hud-val">${fmt(low)}</span></span>
      <span>C: <span class="hud-val">${fmt(close)}</span></span>
      <span>VOL: <span class="hud-val">${fmtVol(vol)}</span></span>
      <span class="${chgClass}">${sign}${fmt(chg)} (${sign}${chgPct.toFixed(2)}%)</span>
    `;
  }

  initChart() {
    if (typeof LightweightCharts === 'undefined') {
      console.error('TradingView LightweightCharts library not found');
      return;
    }

    const w = this.container.clientWidth || 800;
    const h = this.container.clientHeight || 450;
    const tz = this.timeZoneMode === 'UTC' ? 'UTC' : 'America/New_York';
    const tzSuffix = this.timeZoneMode === 'UTC' ? ' UTC' : ' ET';

    this.chart = LightweightCharts.createChart(this.container, {
      width: w,
      height: h,
      localization: {
        locale: 'en-US',
        dateFormat: 'yyyy-MM-dd',
        timeFormatter: (ts) => {
          if (!ts) return '';
          const d = typeof ts === 'number' ? new Date(ts * 1000) : new Date(ts.year, ts.month - 1, ts.day);
          return d.toLocaleTimeString('en-US', {
            timeZone: tz,
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
          }) + tzSuffix;
        },
      },
      layout: {
        background: { type: 'solid', color: '#0a0a0a' },
        textColor: '#ffb000',
        fontFamily: 'Consolas, "Courier New", Courier, monospace',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(255, 176, 0, 0.05)', style: 1 },
        horzLines: { color: 'rgba(255, 176, 0, 0.05)', style: 1 },
      },
      crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: {
          color: '#ffb000',
          width: 1,
          style: LightweightCharts.LineStyle.Dashed,
          labelBackgroundColor: '#332300',
        },
        horzLine: {
          color: '#ffb000',
          width: 1,
          style: LightweightCharts.LineStyle.Dashed,
          labelBackgroundColor: '#332300',
        },
      },
      rightPriceScale: {
        borderColor: '#332300',
        textColor: '#ffb000',
        scaleMargins: {
          top: 0.08,
          bottom: 0.22,
        },
      },
      timeScale: {
        borderColor: '#332300',
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 12,
        barSpacing: 6,
        minBarSpacing: 1,
        tickMarkFormatter: (time, tickMarkType, locale) => {
          if (!time) return '';
          const d = typeof time === 'number' ? new Date(time * 1000) : new Date(time.year, time.month - 1, time.day);
          if (tickMarkType === 0) {
            return d.getFullYear().toString();
          } else if (tickMarkType === 1) {
            return d.toLocaleDateString('en-US', { timeZone: tz, month: 'short' });
          } else if (tickMarkType === 2) {
            return d.toLocaleDateString('en-US', { timeZone: tz, month: 'numeric', day: 'numeric' });
          } else {
            return d.toLocaleTimeString('en-US', {
              timeZone: tz,
              hour12: false,
              hour: '2-digit',
              minute: '2-digit'
            });
          }
        },
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    // 1. Candlestick Series (Bloomberg CRT Theme: Green Up, Red Down)
    this.candleSeries = this.chart.addCandlestickSeries({
      upColor: '#00ff66',
      downColor: '#ff3344',
      borderVisible: true,
      borderUpColor: '#00cc52',
      borderDownColor: '#cc2936',
      wickUpColor: '#00ff66',
      wickDownColor: '#ff3344',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    });

    // 2. Volume Series (Subtle amber/green/red volume bars at the bottom)
    this.volumeSeries = this.chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: '', // overlay inside main area
    });
    this.volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    // Crosshair inspection updates HUD
    this.chart.subscribeCrosshairMove((param) => {
      if (!param || !param.time || !param.seriesData || !param.seriesData.has(this.candleSeries)) {
        this.updateHud(null);
        return;
      }
      const data = param.seriesData.get(this.candleSeries);
      this.updateHud(data);
    });
  }

  // Sanitizes, deduplicates, and validates candle records strictly ascending by time
  sanitizeCandles(rawCandles) {
    if (!rawCandles || !Array.isArray(rawCandles)) return [];
    const map = new Map();

    for (const c of rawCandles) {
      if (!c || c.time === undefined || c.open === undefined || isNaN(c.open)) continue;
      let t = Math.floor(c.time > 1e11 ? c.time / 1000 : c.time);
      if (isNaN(t) || t <= 0) continue;

      const open = Number(c.open);
      const high = Number(c.high);
      const low = Number(c.low);
      const close = Number(c.close);
      const volume = Number(c.volume || 0);

      // Overwrite duplicate timestamps with latest
      map.set(t, {
        time: t,
        open: open,
        high: Math.max(open, high, low, close),
        low: Math.min(open, high, low, close),
        close: close,
        volume: volume
      });
    }

    const sorted = Array.from(map.values()).sort((a, b) => a.time - b.time);
    return sorted;
  }

  aggregateCandles(rawCandles, interval) {
    if (!rawCandles || rawCandles.length === 0) return [];
    if (interval === '1M') return rawCandles;

    // Check if rawCandles is already sampled at or coarser than requested interval
    if (rawCandles.length >= 2) {
      const dt = Math.abs(rawCandles[1].time - rawCandles[0].time);
      if (interval === '5M' && dt >= 240) return rawCandles;
      if (interval === '15M' && dt >= 700) return rawCandles;
      if (interval === '1H' && dt >= 3000) return rawCandles;
      if (interval === '1D' && dt >= 20000) return rawCandles;
    }

    let groupSeconds = 300;
    if (interval === '5M') groupSeconds = 300;
    else if (interval === '15M') groupSeconds = 900;
    else if (interval === '1H') groupSeconds = 3600;
    else if (interval === '1D') groupSeconds = 86400;

    const buckets = new Map();
    for (const bar of rawCandles) {
      const bTime = Math.floor(bar.time / groupSeconds) * groupSeconds;
      if (!buckets.has(bTime)) {
        buckets.set(bTime, {
          time: bTime,
          open: bar.open,
          high: bar.high,
          low: bar.low,
          close: bar.close,
          volume: bar.volume || 0
        });
      } else {
        const b = buckets.get(bTime);
        b.high = Math.max(b.high, bar.high);
        b.low = Math.min(b.low, bar.low);
        b.close = bar.close;
        b.volume += (bar.volume || 0);
      }
    }

    return Array.from(buckets.values()).sort((a, b) => a.time - b.time);
  }

  setInterval(interval) {
    this.interval = interval;
    if (this.chart) {
      this.chart.applyOptions({
        timeScale: {
          timeVisible: this.interval !== '1D',
          secondsVisible: false,
        }
      });
    }
  }

  setData(symbol, candles, currentPrice, interval = null) {
    this.symbol = symbol;
    if (interval) this.interval = interval;
    this.rawCandles = this.sanitizeCandles(candles || []);
    this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    this.currentPrice = currentPrice || (this.candles.length ? this.candles[this.candles.length - 1].close : 0);

    if (this.chart) {
      this.chart.applyOptions({
        timeScale: {
          timeVisible: this.interval !== '1D',
          secondsVisible: false,
        }
      });
    }

    this.applySeriesData();

    if (this.chart) {
      this.chart.timeScale().fitContent();
    }
  }

  syncCandles(candles) {
    if (!candles || candles.length === 0) return;
    this.rawCandles = this.sanitizeCandles(candles);
    this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    this.applySeriesData();
  }

  updateLiveTick(price, size, timestamp) {
    if (!price || isNaN(price)) return;
    this.currentPrice = Number(price);

    const ts = timestamp ? (timestamp > 1e11 ? Math.floor(timestamp / 1000) : Math.floor(timestamp)) : Math.floor(Date.now() / 1000);

    let bucketDuration = 60;
    if (this.interval === '5M') bucketDuration = 300;
    else if (this.interval === '15M') bucketDuration = 900;
    else if (this.interval === '1H') bucketDuration = 3600;
    else if (this.interval === '1D') bucketDuration = 86400;

    const currentBucketTime = Math.floor(ts / bucketDuration) * bucketDuration;

    if (!this.candles || this.candles.length === 0) {
      const initialBar = {
        time: currentBucketTime,
        open: this.currentPrice,
        high: this.currentPrice,
        low: this.currentPrice,
        close: this.currentPrice,
        volume: Number(size || 1)
      };
      this.candles = [initialBar];
      this.rawCandles = [initialBar];
      this.applySeriesData();
      return;
    }

    const last = this.candles[this.candles.length - 1];
    let updatedBar = null;

    if (currentBucketTime > last.time) {
      // New bar for the active interval
      const newBar = {
        time: currentBucketTime,
        open: this.currentPrice,
        high: this.currentPrice,
        low: this.currentPrice,
        close: this.currentPrice,
        volume: Number(size || 1)
      };
      this.candles.push(newBar);
      if (this.candles.length > 5000) {
        this.candles.shift();
      }
      updatedBar = newBar;
    } else {
      // Update existing bar
      last.high = Math.max(last.high, this.currentPrice);
      last.low = Math.min(last.low, this.currentPrice);
      last.close = this.currentPrice;
      last.volume = (last.volume || 0) + Number(size || 0);
      updatedBar = last;
    }

    // High performance O(1) live update
    if (this.candleSeries && updatedBar) {
      this.candleSeries.update(updatedBar);
      if (this.volumeSeries) {
        this.volumeSeries.update({
          time: updatedBar.time,
          value: updatedBar.volume,
          color: updatedBar.close >= updatedBar.open ? 'rgba(0, 255, 102, 0.35)' : 'rgba(255, 51, 68, 0.35)'
        });
      }
      this.updateHud(updatedBar);
    }
  }

  applySeriesData() {
    if (!this.chart || !this.candleSeries) return;

    // Apply Candlesticks
    this.candleSeries.setData(this.candles);

    // Apply Volume
    if (this.volumeSeries) {
      const volData = this.candles.map(c => ({
        time: c.time,
        value: c.volume || 0,
        color: c.close >= c.open ? 'rgba(0, 255, 102, 0.35)' : 'rgba(255, 51, 68, 0.35)'
      }));
      this.volumeSeries.setData(volData);
    }

    // Refresh Indicators
    this.refreshIndicators();

    // Update HUD
    this.updateHud(null);
  }

  toggleIndicator(name) {
    if (!this.indicators.hasOwnProperty(name)) return false;
    this.indicators[name] = !this.indicators[name];
    this.refreshIndicators();
    return this.indicators[name];
  }

  refreshIndicators() {
    if (!this.chart) return;

    // SMA 20
    if (this.indicators.SMA20) {
      if (!this.sma20Series) {
        this.sma20Series = this.chart.addLineSeries({
          color: '#00e5ff',
          lineWidth: 1.5,
          title: 'SMA 20',
        });
      }
      this.sma20Series.setData(this.calculateSMA(20));
    } else if (this.sma20Series) {
      this.chart.removeSeries(this.sma20Series);
      this.sma20Series = null;
    }

    // SMA 50
    if (this.indicators.SMA50) {
      if (!this.sma50Series) {
        this.sma50Series = this.chart.addLineSeries({
          color: '#ff00ea',
          lineWidth: 1.5,
          title: 'SMA 50',
        });
      }
      this.sma50Series.setData(this.calculateSMA(50));
    } else if (this.sma50Series) {
      this.chart.removeSeries(this.sma50Series);
      this.sma50Series = null;
    }

    // Bollinger Bands
    if (this.indicators.BOLL) {
      if (!this.bollUpperSeries) {
        this.bollUpperSeries = this.chart.addLineSeries({
          color: '#ffb000',
          lineWidth: 1,
          lineStyle: LightweightCharts.LineStyle.Dashed,
          title: 'BOLL UP',
        });
        this.bollLowerSeries = this.chart.addLineSeries({
          color: '#ffb000',
          lineWidth: 1,
          lineStyle: LightweightCharts.LineStyle.Dashed,
          title: 'BOLL DN',
        });
        this.bollMidSeries = this.chart.addLineSeries({
          color: 'rgba(255, 176, 0, 0.45)',
          lineWidth: 1,
          lineStyle: LightweightCharts.LineStyle.Dotted,
          title: 'BOLL MID',
        });
      }
      const { upper, lower, mid } = this.calculateBollinger(20, 2.0);
      this.bollUpperSeries.setData(upper);
      this.bollLowerSeries.setData(lower);
      this.bollMidSeries.setData(mid);
    } else if (this.bollUpperSeries) {
      this.chart.removeSeries(this.bollUpperSeries);
      this.chart.removeSeries(this.bollLowerSeries);
      this.chart.removeSeries(this.bollMidSeries);
      this.bollUpperSeries = null;
      this.bollLowerSeries = null;
      this.bollMidSeries = null;
    }

    // RSI 14
    if (this.indicators.RSI) {
      if (!this.rsiSeries) {
        this.rsiSeries = this.chart.addLineSeries({
          color: '#ffea00',
          lineWidth: 1.5,
          priceScaleId: 'rsi',
          title: 'RSI 14',
        });
        this.chart.priceScale('rsi').applyOptions({
          scaleMargins: {
            top: 0.75,
            bottom: 0.02,
          },
        });
        this.rsiSeries.createPriceLine({ price: 70, color: 'rgba(255, 51, 68, 0.5)', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, title: '70' });
        this.rsiSeries.createPriceLine({ price: 30, color: 'rgba(0, 255, 102, 0.5)', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, title: '30' });
      }
      this.rsiSeries.setData(this.calculateRSI(14));
    } else if (this.rsiSeries) {
      this.chart.removeSeries(this.rsiSeries);
      this.rsiSeries = null;
    }

    // MACD
    if (this.indicators.MACD) {
      if (!this.macdHistSeries) {
        this.macdHistSeries = this.chart.addHistogramSeries({
          priceScaleId: 'macd',
          title: 'MACD Hist',
        });
        this.macdLineSeries = this.chart.addLineSeries({
          color: '#00e5ff',
          lineWidth: 1.5,
          priceScaleId: 'macd',
          title: 'MACD',
        });
        this.macdSignalSeries = this.chart.addLineSeries({
          color: '#ff3344',
          lineWidth: 1.5,
          priceScaleId: 'macd',
          title: 'Signal',
        });
        this.chart.priceScale('macd').applyOptions({
          scaleMargins: {
            top: 0.75,
            bottom: 0.02,
          },
        });
      }
      const { macd, signal, hist } = this.calculateMACD();
      this.macdHistSeries.setData(hist);
      this.macdLineSeries.setData(macd);
      this.macdSignalSeries.setData(signal);
    } else if (this.macdHistSeries) {
      this.chart.removeSeries(this.macdHistSeries);
      this.chart.removeSeries(this.macdLineSeries);
      this.chart.removeSeries(this.macdSignalSeries);
      this.macdHistSeries = null;
      this.macdLineSeries = null;
      this.macdSignalSeries = null;
    }
  }

  calculateSMA(period) {
    const data = [];
    if (this.candles.length < period) return data;

    for (let i = period - 1; i < this.candles.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += this.candles[i - j].close;
      }
      data.push({
        time: this.candles[i].time,
        value: sum / period,
      });
    }
    return data;
  }

  calculateBollinger(period = 20, multiplier = 2.0) {
    const upper = [];
    const lower = [];
    const mid = [];
    if (this.candles.length < period) return { upper, lower, mid };

    for (let i = period - 1; i < this.candles.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += this.candles[i - j].close;
      }
      const mean = sum / period;

      let variance = 0;
      for (let j = 0; j < period; j++) {
        variance += Math.pow(this.candles[i - j].close - mean, 2);
      }
      const stdDev = Math.sqrt(variance / period);

      const time = this.candles[i].time;
      mid.push({ time, value: mean });
      upper.push({ time, value: mean + multiplier * stdDev });
      lower.push({ time, value: mean - multiplier * stdDev });
    }
    return { upper, lower, mid };
  }

  calculateRSI(period = 14) {
    const rsi = [];
    if (this.candles.length <= period) return rsi;

    let gains = 0;
    let losses = 0;

    for (let i = 1; i <= period; i++) {
      const diff = this.candles[i].close - this.candles[i - 1].close;
      if (diff > 0) gains += diff;
      else losses += -diff;
    }

    let avgGain = gains / period;
    let avgLoss = losses / period;
    let rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    rsi.push({
      time: this.candles[period].time,
      value: 100 - (100 / (1 + rs)),
    });

    for (let i = period + 1; i < this.candles.length; i++) {
      const diff = this.candles[i].close - this.candles[i - 1].close;
      const gain = diff > 0 ? diff : 0;
      const loss = diff < 0 ? -diff : 0;

      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;
      rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
      rsi.push({
        time: this.candles[i].time,
        value: 100 - (100 / (1 + rs)),
      });
    }

    return rsi;
  }

  calculateMACD(fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
    const macd = [];
    const signal = [];
    const hist = [];
    if (this.candles.length < slowPeriod) return { macd, signal, hist };

    const calcEMA = (data, p) => {
      const k = 2 / (p + 1);
      const ema = new Array(data.length);
      let sum = 0;
      for (let i = 0; i < p; i++) sum += data[i];
      let prev = sum / p;
      ema[p - 1] = prev;
      for (let i = p; i < data.length; i++) {
        prev = (data[i] * k) + (prev * (1 - k));
        ema[i] = prev;
      }
      return ema;
    };

    const closes = this.candles.map(c => c.close);
    const fastEMA = calcEMA(closes, fastPeriod);
    const slowEMA = calcEMA(closes, slowPeriod);

    const macdValues = [];
    const macdTimes = [];

    for (let i = slowPeriod - 1; i < this.candles.length; i++) {
      if (fastEMA[i] !== undefined && slowEMA[i] !== undefined) {
        const val = fastEMA[i] - slowEMA[i];
        macdValues.push(val);
        macdTimes.push(this.candles[i].time);
        macd.push({ time: this.candles[i].time, value: val });
      }
    }

    if (macdValues.length >= signalPeriod) {
      const signalEMA = calcEMA(macdValues, signalPeriod);
      for (let i = signalPeriod - 1; i < macdValues.length; i++) {
        const sigVal = signalEMA[i];
        const time = macdTimes[i];
        signal.push({ time, value: sigVal });
        const hVal = macdValues[i] - sigVal;
        hist.push({
          time,
          value: hVal,
          color: hVal >= 0 ? 'rgba(0, 229, 255, 0.6)' : 'rgba(255, 51, 68, 0.6)'
        });
      }
    }

    return { macd, signal, hist };
  }
}
