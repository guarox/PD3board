/*
 * PD3board Hardware-Accelerated 60 FPS HTML5 Canvas Financial Chart
 * Features: Candlesticks, Volume Histograms, Interactive Crosshair,
 * Pan & Zoom, Dynamic Hover Tooltip HUD, Time Interval Switching,
 * Technical Overlays (SMA 20, SMA 50, Bollinger Bands), and RSI Sub-Pane.
 */

class PriceChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!canvasId || !this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.candles = [];
    this.rawCandles = [];
    this.currentPrice = 0;
    this.symbol = 'BTCUSDT';
    this.interval = '1M';

    // Technical Indicators
    this.indicators = {
      SMA20: false,
      SMA50: false,
      BOLL: false,
      RSI: false,
      MACD: false
    };

    // Interactive state: Crosshair, Tooltip, Pan & Zoom
    this.mouse = { x: -1, y: -1, active: false };
    this.isDragging = false;
    this.dragStartX = 0;
    this.panOffset = 0;
    this.zoomLevel = 1.0;

    this.resize();
    this.bindEvents();
    window.addEventListener('resize', () => this.resize());
    if (typeof ResizeObserver !== 'undefined' && this.canvas.parentElement) {
      this.resizeObserver = new ResizeObserver(() => this.resize());
      this.resizeObserver.observe(this.canvas.parentElement);
    }
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;
    this.canvas.width = rect.width * (window.devicePixelRatio || 1);
    this.canvas.height = rect.height * (window.devicePixelRatio || 1);
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
    this.width = rect.width;
    this.height = rect.height;
    this.render();
  }

  bindEvents() {
    if (!this.canvas) return;

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      if (this.isDragging) {
        const dx = x - this.dragStartX;
        this.panOffset += dx;
        this.dragStartX = x;
      }

      this.mouse.x = x;
      this.mouse.y = y;
      this.mouse.active = true;
      this.render();
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.mouse.active = false;
      this.isDragging = false;
      this.render();
    });

    this.canvas.addEventListener('mousedown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.isDragging = true;
      this.dragStartX = e.clientX - rect.left;
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    // Zoom on mouse wheel
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.zoomLevel = Math.max(0.15, Math.min(5.0, this.zoomLevel * zoomFactor));
      this.render();
    }, { passive: false });

    // Double-click resets pan & zoom
    this.canvas.addEventListener('dblclick', () => {
      this.panOffset = 0;
      this.zoomLevel = 1.0;
      this.render();
    });
  }

  toggleIndicator(name) {
    if (this.indicators.hasOwnProperty(name)) {
      this.indicators[name] = !this.indicators[name];
      this.render();
      return this.indicators[name];
    }
    return false;
  }

  calculateSMA(period) {
    const sma = [];
    for (let i = 0; i < this.candles.length; i++) {
      if (i < period - 1) {
        sma.push(null);
      } else {
        let sum = 0;
        for (let j = 0; j < period; j++) {
          sum += this.candles[i - j].close;
        }
        sma.push(sum / period);
      }
    }
    return sma;
  }

  calculateBollinger(period = 20, multiplier = 2.0) {
    const upper = [];
    const lower = [];
    const sma = this.calculateSMA(period);
    for (let i = 0; i < this.candles.length; i++) {
      if (sma[i] === null) {
        upper.push(null);
        lower.push(null);
      } else {
        let variance = 0;
        for (let j = 0; j < period; j++) {
          variance += Math.pow(this.candles[i - j].close - sma[i], 2);
        }
        const stdDev = Math.sqrt(variance / period);
        upper.push(sma[i] + multiplier * stdDev);
        lower.push(sma[i] - multiplier * stdDev);
      }
    }
    return { upper, lower, sma };
  }

  calculateRSI(period = 14) {
    const rsi = [];
    if (this.candles.length < 2) return rsi;

    let gains = 0;
    let losses = 0;

    for (let i = 0; i < this.candles.length; i++) {
      if (i === 0) {
        rsi.push(null);
        continue;
      }
      const diff = this.candles[i].close - this.candles[i - 1].close;
      const gain = diff > 0 ? diff : 0;
      const loss = diff < 0 ? -diff : 0;

      if (i < period) {
        gains += gain;
        losses += loss;
        rsi.push(null);
      } else if (i === period) {
        gains += gain;
        losses += loss;
        const avgGain = gains / period;
        const avgLoss = losses / period;
        if (avgGain === 0 && avgLoss === 0) {
          rsi.push(50.0);
        } else {
          const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
          rsi.push(100 - (100 / (1 + rs)));
        }
      } else {
        const avgGain = (gains * (period - 1) + gain) / period;
        const avgLoss = (losses * (period - 1) + loss) / period;
        gains = avgGain;
        losses = avgLoss;
        if (avgGain === 0 && avgLoss === 0) {
          rsi.push(50.0);
        } else {
          const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
          rsi.push(100 - (100 / (1 + rs)));
        }
      }
    }
    return rsi;
  }

  calculateMACD(fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
    if (this.candles.length < 5) return { macd: [], signal: [], hist: [] };
    const closes = this.candles.map(c => c.close);

    const calcEMA = (data, p) => {
      const k = 2 / (p + 1);
      const ema = new Array(data.length).fill(null);
      let sum = 0;
      const initial = Math.min(p, data.length);
      for (let i = 0; i < initial; i++) sum += data[i];
      let prev = sum / initial;
      ema[initial - 1] = prev;
      for (let i = initial; i < data.length; i++) {
        prev = (data[i] * k) + (prev * (1 - k));
        ema[i] = prev;
      }
      return ema;
    };

    const fastEMA = calcEMA(closes, Math.min(fastPeriod, closes.length));
    const slowEMA = calcEMA(closes, Math.min(slowPeriod, closes.length));
    const macdLine = [];
    for (let i = 0; i < closes.length; i++) {
      if (fastEMA[i] !== null && slowEMA[i] !== null) {
        macdLine.push(fastEMA[i] - slowEMA[i]);
      } else {
        macdLine.push(0);
      }
    }
    const signalLine = calcEMA(macdLine, Math.min(signalPeriod, macdLine.length));
    const hist = [];
    for (let i = 0; i < closes.length; i++) {
      hist.push(macdLine[i] - (signalLine[i] !== null ? signalLine[i] : 0));
    }
    return { macd: macdLine, signal: signalLine, hist: hist };
  }

  aggregateCandles(rawCandles, interval) {
    if (!rawCandles || rawCandles.length === 0) return [];
    if (interval === '1M') return [...rawCandles];

    // Check if rawCandles is already sampled at or coarser than requested interval
    if (rawCandles.length >= 2) {
      const dt0 = Math.abs((rawCandles[1].time || 0) - (rawCandles[0].time || 0));
      const dt = dt0 > 1e10 ? dt0 / 1000 : dt0;
      if (interval === '5M' && dt >= 240) return [...rawCandles];
      if (interval === '15M' && dt >= 700) return [...rawCandles];
      if (interval === '1H' && dt >= 3000) return [...rawCandles];
      if (interval === '1D' && dt >= 20000) return [...rawCandles];
    }

    let groupSize = 5;
    if (interval === '5M') groupSize = 5;
    else if (interval === '15M') groupSize = 15;
    else if (interval === '1H') groupSize = 60;
    else if (interval === '1D') groupSize = 240;

    const aggregated = [];
    for (let i = 0; i < rawCandles.length; i += groupSize) {
      const slice = rawCandles.slice(i, i + groupSize);
      if (slice.length === 0) continue;

      let high = -Infinity;
      let low = Infinity;
      let volume = 0;

      for (const bar of slice) {
        if (bar.high > high) high = bar.high;
        if (bar.low < low) low = bar.low;
        volume += (bar.volume || 0);
      }

      aggregated.push({
        time: slice[0].time,
        open: slice[0].open,
        high: high,
        low: low,
        close: slice[slice.length - 1].close,
        volume: volume
      });
    }
    return aggregated;
  }

  setInterval(interval) {
    this.interval = interval;
    this.panOffset = 0;
    if (this.rawCandles && this.rawCandles.length > 0) {
      this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    }
    this.render();
  }

  setData(symbol, candles, currentPrice, interval = null) {
    this.symbol = symbol;
    if (interval) this.interval = interval;
    this.rawCandles = candles || [];
    this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    this.currentPrice = currentPrice || (this.candles.length ? this.candles[this.candles.length - 1].close : 0);
    this.panOffset = 0;
    this.render();
  }

  syncCandles(candles) {
    if (!candles || candles.length === 0) return;
    this.rawCandles = candles;
    this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    this.render();
  }

  updateLiveTick(price, size, timestamp) {
    if (!price || isNaN(price)) return;
    this.currentPrice = price;

    const ts = timestamp ? (timestamp > 1e11 ? Math.floor(timestamp / 1000) : Math.floor(timestamp)) : Math.floor(Date.now() / 1000);
    const minuteBucket = Math.floor(ts / 60) * 60;

    if (!this.rawCandles || this.rawCandles.length === 0) {
      this.rawCandles = [{
        time: minuteBucket,
        open: price,
        high: price,
        low: price,
        close: price,
        volume: size || 1
      }];
      this.candles = this.aggregateCandles(this.rawCandles, this.interval);
      this.render();
      return;
    }

    const last = this.rawCandles[this.rawCandles.length - 1];
    const lastTime = last.time || 0;
    const lastBucket = lastTime > 1e11 ? Math.floor(lastTime / 1000 / 60) * 60 : Math.floor(lastTime / 60) * 60;

    // Advance to next 1-minute candle bucket when minute boundary passes
    if (minuteBucket > lastBucket && lastBucket > 0) {
      this.rawCandles.push({
        time: minuteBucket,
        open: price,
        high: price,
        low: price,
        close: price,
        volume: size || 1
      });
      if (this.rawCandles.length > 3000) {
        this.rawCandles.shift();
      }
    } else {
      const refPrice = last.close || last.open;
      if (refPrice > 0 && Math.abs(price - refPrice) / refPrice > 0.35) {
        last.open = price;
        last.high = price;
        last.low = price;
        last.close = price;
      } else {
        last.high = Math.max(last.high, price);
        last.low = Math.min(last.low, price);
        last.close = price;
      }
      last.volume = (last.volume || 0) + (size || 0);
    }

    this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    this.render();
  }

  render() {
    if (!this.ctx || this.width === 0 || this.height === 0) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    // Dark Bloomberg CRT canvas background
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, this.width, this.height);

    if (this.candles.length === 0) {
      ctx.fillStyle = '#666';
      ctx.font = '12px monospace';
      ctx.fillText('Awaiting real-time tick stream for ' + this.symbol + '...', 20, 30);
      return;
    }

    // Chart margins
    const marginRight = 70;
    const marginBottom = 25;
    const marginTop = 24;
    const plotWidth = this.width - marginRight;
    const totalPlotHeight = this.height - marginTop - marginBottom;
    // Allocate height if RSI or MACD is enabled
    const rsiActive = this.indicators.RSI;
    const macdActive = this.indicators.MACD;
    const subPaneCount = (rsiActive ? 1 : 0) + (macdActive ? 1 : 0);
    const subPaneHeight = subPaneCount > 0 ? Math.max(40, Math.floor((totalPlotHeight * (subPaneCount === 2 ? 0.36 : 0.22)) / subPaneCount)) : 0;
    const pricePlotHeight = totalPlotHeight - (subPaneCount * (subPaneHeight + 8));

    let currentSubPaneTop = marginTop + pricePlotHeight + 8;
    let rsiTop = 0;
    let rsiHeight = 0;
    if (rsiActive) {
      rsiTop = currentSubPaneTop;
      rsiHeight = subPaneHeight;
      currentSubPaneTop += subPaneHeight + 8;
    }
    let macdTop = 0;
    let macdHeight = 0;
    if (macdActive) {
      macdTop = currentSubPaneTop;
      macdHeight = subPaneHeight;
    }

    // Calculate dynamic candle width with zoom and pan
    const baseCandleWidth = Math.max(2, Math.floor(plotWidth / (Math.min(this.candles.length, 220) * 1.5)));
    const candleWidth = Math.min(32, Math.max(1, Math.floor(baseCandleWidth * this.zoomLevel)));
    const gap = candleWidth > 2 ? Math.max(1, Math.floor(candleWidth * 0.35)) : (candleWidth > 1 ? 1 : 0);
    const totalCandleSpan = Math.max(1, candleWidth + gap);

    // Bounded pan offset and right-alignment (anchors latest bars to the right edge)
    const totalContentWidth = this.candles.length * totalCandleSpan;
    const rightAlignOffset = plotWidth - totalContentWidth - 10;
    const minPan = -30;
    const maxPan = Math.max(0, totalContentWidth - plotWidth + 30);
    this.panOffset = Math.max(minPan, Math.min(maxPan, this.panOffset));

    // Calculate High / Low range for visible candles in current viewport
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVol = 0;
    let visibleCount = 0;

    for (let i = 0; i < this.candles.length; i++) {
      const c = this.candles[i];
      const rawX = rightAlignOffset + i * totalCandleSpan + this.panOffset;
      if (rawX + candleWidth >= -20 && rawX <= plotWidth + 20) {
        if (c.low < minPrice) minPrice = c.low;
        if (c.high > maxPrice) maxPrice = c.high;
        if (c.volume > maxVol) maxVol = c.volume;
        visibleCount++;
      }
    }

    if (visibleCount === 0 || !isFinite(minPrice) || !isFinite(maxPrice)) {
      for (const c of this.candles) {
        if (c.low < minPrice) minPrice = c.low;
        if (c.high > maxPrice) maxPrice = c.high;
        if (c.volume > maxVol) maxVol = c.volume;
      }
    }

    if (this.currentPrice > 0 && this.panOffset <= 50) {
      minPrice = Math.min(minPrice, this.currentPrice);
      maxPrice = Math.max(maxPrice, this.currentPrice);
    }

    if (!isFinite(minPrice) || !isFinite(maxPrice)) {
      minPrice = 0;
      maxPrice = 100;
    }

    // Proportional padding based on actual price magnitude and range
    const rawRange = (maxPrice - minPrice);
    let padding = 0;
    if (rawRange <= 0.000001) {
      padding = maxPrice > 0 ? maxPrice * 0.02 : 1.0;
    } else {
      padding = Math.max(rawRange * 0.08, maxPrice * 0.0005);
    }
    minPrice -= padding;
    maxPrice += padding;
    if (maxPrice <= minPrice) {
      minPrice -= 1;
      maxPrice += 1;
    }

    const priceSpan = maxPrice - minPrice;
    const priceToY = (p) => marginTop + pricePlotHeight - ((p - minPrice) / (priceSpan || 1)) * pricePlotHeight;
    const yToPrice = (y) => maxPrice - ((y - marginTop) / (pricePlotHeight || 1)) * priceSpan;

    // Dynamic price formatting precision
    const getDecimals = (val, span) => {
      const p = Math.abs(val || 0);
      const s = Math.abs(span || 1);
      if (s < 0.0005 || p < 0.01) return 5;
      if (s < 0.005 || p < 0.5) return 4;
      if (s < 0.05 || p < 2.0) return 4;
      if (s < 0.5 || p < 20.0) return 3;
      return 2;
    };
    const precision = getDecimals(this.currentPrice || maxPrice, priceSpan);
    const formatP = (val, prec = precision) => {
      if (val === null || val === undefined || isNaN(val)) return '0.00';
      return Number(val).toLocaleString('en-US', {
        minimumFractionDigits: prec,
        maximumFractionDigits: prec
      });
    };

    // Draw Grid Lines & Price Axis
    ctx.strokeStyle = '#1e1a0d';
    ctx.lineWidth = 1;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#996a00';

    const gridSteps = 5;
    for (let i = 0; i <= gridSteps; i++) {
      const y = marginTop + (pricePlotHeight / gridSteps) * i;
      const p = maxPrice - (priceSpan / gridSteps) * i;

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(plotWidth, y);
      ctx.stroke();

      ctx.fillText(formatP(p), plotWidth + 6, y + 3);
    }

    // Bollinger Bands Calculation & Rendering
    if (this.indicators.BOLL && this.candles.length >= 5) {
      const bollPeriod = Math.min(20, this.candles.length);
      const boll = this.calculateBollinger(bollPeriod, 2.0);

      // Shaded area between upper and lower band
      ctx.fillStyle = 'rgba(255, 176, 0, 0.07)';
      ctx.beginPath();
      let first = true;
      for (let i = 0; i < this.candles.length; i++) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (boll.upper[i] !== null && x >= -10 && x <= plotWidth + 10) {
          const y = priceToY(boll.upper[i]);
          if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
        }
      }
      for (let i = this.candles.length - 1; i >= 0; i--) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (boll.lower[i] !== null && x >= -10 && x <= plotWidth + 10) {
          ctx.lineTo(x, priceToY(boll.lower[i]));
        }
      }
      ctx.closePath();
      ctx.fill();

      // Draw upper and lower lines
      ctx.strokeStyle = 'rgba(255, 176, 0, 0.45)';
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 2]);

      ctx.beginPath();
      first = true;
      for (let i = 0; i < this.candles.length; i++) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (boll.upper[i] !== null && x >= -10 && x <= plotWidth + 10) {
          const y = priceToY(boll.upper[i]);
          if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
        }
      }
      ctx.stroke();

      ctx.beginPath();
      first = true;
      for (let i = 0; i < this.candles.length; i++) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (boll.lower[i] !== null && x >= -10 && x <= plotWidth + 10) {
          const y = priceToY(boll.lower[i]);
          if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
        }
      }
      ctx.stroke();
      ctx.setLineDash([]);
    }

    let hoveredCandle = null;
    let hoveredX = -1;

    // Draw Candles, Volume Bars & Time Labels
    for (let i = 0; i < this.candles.length; i++) {
      const c = this.candles[i];
      const rawX = rightAlignOffset + i * totalCandleSpan + this.panOffset;
      if (rawX + candleWidth < 0 || rawX > plotWidth) continue;

      const candleX = Math.floor(rawX);
      const cWidth = Math.max(2, Math.floor(candleWidth));
      const wickX = candleX + Math.floor(cWidth / 2) + 0.5;

      const isUp = c.close >= c.open;
      const candleColor = isUp ? '#00ff66' : '#ff3344';
      const candleBorder = isUp ? '#00cc52' : '#cc2936';

      // Subtle vertical grid line and time marking every 8-10 candles
      const stepCandles = Math.max(6, Math.floor(75 / totalCandleSpan));
      if (i % stepCandles === 0 && c.time) {
        ctx.strokeStyle = '#181409';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(wickX, marginTop);
        ctx.lineTo(wickX, marginTop + pricePlotHeight);
        ctx.stroke();

        const tsSec = c.time > 1e11 ? Math.floor(c.time / 1000) : Math.floor(c.time);
        const d = new Date(tsSec * 1000);
        let timeLabel = '';
        if (this.interval === '1D') {
          const m = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][d.getMonth()];
          timeLabel = `${m} ${d.getDate()}`;
        } else if (this.interval === '1H') {
          const m = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][d.getMonth()];
          timeLabel = `${m} ${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:00`;
        } else {
          const hh = String(d.getHours()).padStart(2, '0');
          const mm = String(d.getMinutes()).padStart(2, '0');
          timeLabel = `${hh}:${mm}`;
        }
        ctx.font = '9px monospace';
        ctx.fillStyle = '#886200';
        ctx.fillText(timeLabel, Math.max(0, Math.min(plotWidth - 55, wickX - 16)), marginTop + pricePlotHeight + 14);
      }

      // Scaled Volume bar at bottom of price plot
      const volHeight = maxVol > 0 ? (c.volume / maxVol) * (pricePlotHeight * 0.18) : 0;
      ctx.fillStyle = isUp ? 'rgba(0, 255, 102, 0.28)' : 'rgba(255, 51, 68, 0.28)';
      ctx.fillRect(candleX, Math.floor(marginTop + pricePlotHeight - volHeight), cWidth, Math.ceil(volHeight));

      // Pixel Y coordinates
      const yHigh = Math.round(priceToY(c.high));
      const yLow = Math.round(priceToY(c.low));
      const yOpen = Math.round(priceToY(c.open));
      const yClose = Math.round(priceToY(c.close));

      const bodyTop = Math.min(yOpen, yClose);
      const bodyBottom = Math.max(yOpen, yClose);
      const bodyHeight = Math.max(bodyBottom - bodyTop, 1);

      // Candlestick Wicks (Upper & Lower)
      ctx.strokeStyle = candleColor;
      ctx.lineWidth = 1;
      ctx.beginPath();
      if (yHigh < bodyTop) {
        ctx.moveTo(wickX, yHigh);
        ctx.lineTo(wickX, bodyTop);
      }
      if (yLow > bodyBottom) {
        ctx.moveTo(wickX, bodyBottom);
        ctx.lineTo(wickX, yLow);
      }
      ctx.stroke();

      // Candlestick Body
      ctx.fillStyle = candleColor;
      ctx.fillRect(candleX, bodyTop, cWidth, bodyHeight);

      // Clean border outline if candle is wide enough
      if (cWidth >= 5 && bodyHeight >= 3) {
        ctx.strokeStyle = candleBorder;
        ctx.strokeRect(candleX + 0.5, bodyTop + 0.5, cWidth - 1, bodyHeight - 1);
      }

      // Check mouse hover
      if (this.mouse.active && this.mouse.x >= candleX - gap / 2 && this.mouse.x <= candleX + cWidth + gap / 2) {
        hoveredCandle = c;
        hoveredX = wickX;
      }
    }

    // SMA 20 Overlay Line (Cyan)
    if (this.indicators.SMA20 && this.candles.length >= 5) {
      const period = Math.min(20, this.candles.length);
      const sma = this.calculateSMA(period);
      ctx.strokeStyle = '#00e5ff';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      let first = true;
      for (let i = 0; i < this.candles.length; i++) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (sma[i] !== null && x >= -10 && x <= plotWidth + 10) {
          const y = priceToY(sma[i]);
          if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
        }
      }
      ctx.stroke();
    }

    // SMA 50 Overlay Line (Magenta)
    if (this.indicators.SMA50 && this.candles.length >= 10) {
      const period = Math.min(50, this.candles.length);
      const sma = this.calculateSMA(period);
      ctx.strokeStyle = '#ff00ea';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      let first = true;
      for (let i = 0; i < this.candles.length; i++) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (sma[i] !== null && x >= -10 && x <= plotWidth + 10) {
          const y = priceToY(sma[i]);
          if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
        }
      }
      ctx.stroke();
    }

    // RSI Sub-Pane
    if (rsiActive && rsiHeight > 0) {
      const rsiValues = this.calculateRSI(14);
      const rsiToY = (v) => rsiTop + rsiHeight - (v / 100) * rsiHeight;

      // Background & Boundary
      ctx.fillStyle = '#060606';
      ctx.fillRect(0, rsiTop, plotWidth, rsiHeight);
      ctx.strokeStyle = '#221800';
      ctx.strokeRect(0, rsiTop, plotWidth, rsiHeight);

      // 70 Line (Overbought)
      ctx.strokeStyle = 'rgba(255, 51, 68, 0.4)';
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(0, rsiToY(70));
      ctx.lineTo(plotWidth, rsiToY(70));
      ctx.stroke();

      // 30 Line (Oversold)
      ctx.strokeStyle = 'rgba(0, 255, 102, 0.4)';
      ctx.beginPath();
      ctx.moveTo(0, rsiToY(30));
      ctx.lineTo(plotWidth, rsiToY(30));
      ctx.stroke();

      // 50 Centerline
      ctx.strokeStyle = 'rgba(153, 106, 0, 0.25)';
      ctx.beginPath();
      ctx.moveTo(0, rsiToY(50));
      ctx.lineTo(plotWidth, rsiToY(50));
      ctx.stroke();
      ctx.setLineDash([]);

      // RSI Labels on Right Margin
      ctx.font = '9px monospace';
      ctx.fillStyle = '#ff3344';
      ctx.fillText('70', plotWidth + 6, rsiToY(70) + 3);
      ctx.fillStyle = '#00ff66';
      ctx.fillText('30', plotWidth + 6, rsiToY(30) + 3);

      // Draw RSI Curve
      ctx.strokeStyle = '#ffb000';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      let first = true;
      let latestRsi = 50.0;
      for (let i = 0; i < this.candles.length; i++) {
        const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
        if (rsiValues[i] !== null && x >= -10 && x <= plotWidth + 10) {
          const y = rsiToY(rsiValues[i]);
          latestRsi = rsiValues[i];
          if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
        }
      }
      ctx.stroke();

      // Live Badge
      ctx.font = 'bold 9px monospace';
      ctx.fillStyle = '#ffb000';
      ctx.fillText(`RSI(14): ${latestRsi.toFixed(1)}`, 8, rsiTop + 12);
    }

    // MACD Sub-Pane
    if (macdActive && macdHeight > 0) {
      const macdData = this.calculateMACD(12, 26, 9);
      const { macd, signal, hist } = macdData;

      let latestMacd = 0;
      let latestSignal = 0;

      if (macd && macd.length > 0) {
        // Find max abs amplitude for symmetric scale around 0
        let maxAmp = 0.001;
        for (let i = 0; i < this.candles.length; i++) {
          if (macd[i] != null && Math.abs(macd[i]) > maxAmp) maxAmp = Math.abs(macd[i]);
          if (signal && signal[i] != null && Math.abs(signal[i]) > maxAmp) maxAmp = Math.abs(signal[i]);
          if (hist && hist[i] != null && Math.abs(hist[i]) > maxAmp) maxAmp = Math.abs(hist[i]);
        }
        maxAmp *= 1.15; // 15% headroom

        const zeroY = macdTop + macdHeight / 2;
        const macdToY = (v) => zeroY - (v / maxAmp) * (macdHeight / 2);

        // Background & Boundary
        ctx.fillStyle = '#060606';
        ctx.fillRect(0, macdTop, plotWidth, macdHeight);
        ctx.strokeStyle = '#221800';
        ctx.strokeRect(0, macdTop, plotWidth, macdHeight);

        // Zero Baseline
        ctx.strokeStyle = 'rgba(153, 106, 0, 0.4)';
        ctx.beginPath();
        ctx.moveTo(0, zeroY);
        ctx.lineTo(plotWidth, zeroY);
        ctx.stroke();

        // Zero Label on Right Margin
        ctx.font = '9px monospace';
        ctx.fillStyle = '#888';
        ctx.fillText('0.00', plotWidth + 6, zeroY + 3);

        // Draw Histogram Bars
        if (hist) {
          for (let i = 0; i < this.candles.length; i++) {
            const x = rightAlignOffset + i * totalCandleSpan + this.panOffset;
            if (x + candleWidth < 0 || x > plotWidth) continue;
            const hVal = hist[i] || 0;
            const barH = (hVal / maxAmp) * (macdHeight / 2);
            ctx.fillStyle = hVal >= 0 ? 'rgba(0, 255, 102, 0.6)' : 'rgba(255, 51, 68, 0.6)';
            if (hVal >= 0) {
              ctx.fillRect(x, zeroY - barH, candleWidth, barH);
            } else {
              ctx.fillRect(x, zeroY, candleWidth, -barH);
            }
          }
        }

        // Draw MACD Line (Cyan)
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        let first = true;
        for (let i = 0; i < this.candles.length; i++) {
          const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
          const mVal = macd[i];
          if (typeof mVal === 'number' && !isNaN(mVal) && x >= -10 && x <= plotWidth + 10) {
            const y = macdToY(mVal);
            latestMacd = mVal;
            if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
          }
        }
        ctx.stroke();

        // Draw Signal Line (Amber)
        if (signal) {
          ctx.strokeStyle = '#ffb000';
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          first = true;
          for (let i = 0; i < this.candles.length; i++) {
            const x = rightAlignOffset + i * totalCandleSpan + this.panOffset + candleWidth / 2;
            const sVal = signal[i];
            if (typeof sVal === 'number' && !isNaN(sVal) && x >= -10 && x <= plotWidth + 10) {
              const y = macdToY(sVal);
              latestSignal = sVal;
              if (first) { ctx.moveTo(x, y); first = false; } else { ctx.lineTo(x, y); }
            }
          }
          ctx.stroke();
        }
      }

      // Live Badge
      ctx.font = 'bold 9px monospace';
      ctx.fillStyle = '#00f0ff';
      const macdBadge = (typeof latestMacd === 'number' && !isNaN(latestMacd)) ? latestMacd.toFixed(2) : '0.00';
      const sigBadge = (typeof latestSignal === 'number' && !isNaN(latestSignal)) ? latestSignal.toFixed(2) : '0.00';
      ctx.fillText(`MACD(12,26): ${macdBadge}`, 8, macdTop + 12);
      ctx.fillStyle = '#ffb000';
      ctx.fillText(`SIG(9): ${sigBadge}`, 140, macdTop + 12);
    }

    // Current Price Dashed Reference Line
    if (this.currentPrice > 0) {
      const liveY = priceToY(this.currentPrice);
      if (liveY >= marginTop && liveY <= marginTop + pricePlotHeight) {
        ctx.strokeStyle = '#ffb000';
        ctx.setLineDash([4, 2]);
        ctx.beginPath();
        ctx.moveTo(0, liveY);
        ctx.lineTo(plotWidth, liveY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Current Price Label Badge
        ctx.fillStyle = '#ffb000';
        ctx.fillRect(plotWidth, liveY - 9, marginRight, 18);
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 10px monospace';
        ctx.fillText(formatP(this.currentPrice), plotWidth + 4, liveY + 4);
      }
    }

    // Interactive Crosshair & Tooltip HUD
    if (this.mouse.active && this.mouse.x <= plotWidth && this.mouse.y >= marginTop && this.mouse.y <= marginTop + totalPlotHeight) {
      const crossX = hoveredX > 0 ? hoveredX : this.mouse.x;
      const crossY = this.mouse.y;

      ctx.strokeStyle = 'rgba(255, 176, 0, 0.45)';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);

      // Vertical line
      ctx.beginPath();
      ctx.moveTo(crossX, marginTop);
      ctx.lineTo(crossX, marginTop + totalPlotHeight);
      ctx.stroke();

      // Horizontal line
      if (crossY <= marginTop + pricePlotHeight) {
        ctx.beginPath();
        ctx.moveTo(0, crossY);
        ctx.lineTo(plotWidth, crossY);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      // Price indicator on Y-axis
      if (crossY <= marginTop + pricePlotHeight) {
        const hoverPrice = yToPrice(crossY);
        ctx.fillStyle = '#ffcc00';
        ctx.fillRect(plotWidth, crossY - 8, marginRight, 16);
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 9px monospace';
        ctx.fillText(formatP(hoverPrice), plotWidth + 4, crossY + 4);
      }

      // Top HUD Bar showing candle metrics
      if (hoveredCandle) {
        const c = hoveredCandle;
        const chg = c.close - c.open;
        const chgPct = (c.open > 0) ? (chg / c.open) * 100 : 0;
        const chgColor = chg >= 0 ? '#00ff66' : '#ff3344';
        const sign = chg >= 0 ? '+' : '';

        ctx.fillStyle = '#111111';
        ctx.fillRect(0, 0, plotWidth, marginTop);
        ctx.strokeStyle = '#332300';
        ctx.strokeRect(0, 0, plotWidth, marginTop);

        ctx.font = 'bold 11px monospace';
        ctx.fillStyle = '#ffb000';
        let tx = 8;
        ctx.fillText(this.symbol, tx, 16); tx += 65;

        ctx.font = '10px monospace';
        ctx.fillStyle = '#888';
        ctx.fillText('O:', tx, 16); tx += 15;
        ctx.fillStyle = '#fff';
        ctx.fillText(formatP(c.open), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('H:', tx, 16); tx += 15;
        ctx.fillStyle = '#00ff66';
        ctx.fillText(formatP(c.high), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('L:', tx, 16); tx += 15;
        ctx.fillStyle = '#ff3344';
        ctx.fillText(formatP(c.low), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('C:', tx, 16); tx += 15;
        ctx.fillStyle = '#fff';
        ctx.fillText(formatP(c.close), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('CHG:', tx, 16); tx += 28;
        ctx.fillStyle = chgColor;
        ctx.fillText(`${sign}${formatP(chg)} (${sign}${chgPct.toFixed(2)}%)`, tx, 16); tx += 95;

        ctx.fillStyle = '#888';
        ctx.fillText('VOL:', tx, 16); tx += 28;
        ctx.fillStyle = '#ffcc00';
        ctx.fillText(Math.round(c.volume).toLocaleString(), tx, 16); tx += 55;

        if (c.time) {
          const tsSec = c.time > 1e11 ? Math.floor(c.time / 1000) : Math.floor(c.time);
          const d = new Date(tsSec * 1000);
          let hudTime = '';
          if (this.interval === '1D') {
            const m = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][d.getMonth()];
            hudTime = `${m} ${d.getDate()}, ${d.getFullYear()}`;
          } else if (this.interval === '1H') {
            const m = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][d.getMonth()];
            hudTime = `${m} ${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
          } else {
            const hh = String(d.getHours()).padStart(2, '0');
            const mm = String(d.getMinutes()).padStart(2, '0');
            hudTime = `${hh}:${mm}`;
          }
          ctx.fillStyle = '#888';
          ctx.fillText('TIME:', tx, 16); tx += 32;
          ctx.fillStyle = '#00e5ff';
          ctx.fillText(hudTime, tx, 16);
        }
      }
    } else {
      // Default top info bar when not hovering
      ctx.fillStyle = '#111111';
      ctx.fillRect(0, 0, plotWidth, marginTop);
      ctx.strokeStyle = '#222';
      ctx.strokeRect(0, 0, plotWidth, marginTop);

      ctx.font = 'bold 11px monospace';
      ctx.fillStyle = '#ffb000';
      const timeframeTitle = this.interval === '1D' ? 'DAILY HISTORICAL (1Y)' : (this.interval === '1H' ? 'HOURLY TREND (3M)' : (this.interval === '15M' ? '15M TREND (1M)' : (this.interval === '5M' ? '5M INTRADAY (5D)' : '1M INTRADAY ACTION (60 FPS)')));
      let title = `${this.symbol} [${this.interval}] ${timeframeTitle}`;
      const activeInds = Object.keys(this.indicators).filter(k => this.indicators[k]);
      if (activeInds.length > 0) {
        title += ` // ${activeInds.join(', ')}`;
      }
      ctx.fillText(title, 8, 16);

      ctx.font = '10px monospace';
      ctx.fillStyle = '#888';
      ctx.fillText('DOUBLE-CLICK RESET / DRAG PAN', plotWidth - 200, 16);
    }
  }
}

window.PriceChart = PriceChart;
