/*
 * PD3board Hardware-Accelerated 60 FPS HTML5 Canvas Financial Chart
 * Features: Candlesticks, Volume Histograms, Interactive Crosshair,
 * Pan & Zoom, Dynamic Hover Tooltip HUD, and Time Interval Switching.
 */

class PriceChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!canvasId || !this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.candles = [];
    this.currentPrice = 0;
    this.symbol = 'BTCUSDT';
    this.interval = '1M';

    // Interactive state: Crosshair, Tooltip, Pan & Zoom
    this.mouse = { x: -1, y: -1, active: false };
    this.isDragging = false;
    this.dragStartX = 0;
    this.panOffset = 0;
    this.zoomLevel = 1.0; // 1.0 = normal, < 1.0 = zoomed out, > 1.0 = zoomed in

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
      this.zoomLevel = Math.max(0.5, Math.min(3.0, this.zoomLevel * zoomFactor));
      this.render();
    }, { passive: false });

    // Double-click resets pan & zoom
    this.canvas.addEventListener('dblclick', () => {
      this.panOffset = 0;
      this.zoomLevel = 1.0;
      this.render();
    });
  }

  aggregateCandles(rawCandles, interval) {
    if (!rawCandles || rawCandles.length === 0) return [];
    if (interval === '1M') return [...rawCandles];

    let groupSize = 5;
    if (interval === '5M') groupSize = 5;
    else if (interval === '15M') groupSize = 15;
    else if (interval === '1H') groupSize = 30;
    else if (interval === '1D') groupSize = 60;

    const aggregated = [];
    for (let i = 0; i < rawCandles.length; i += groupSize) {
      const chunk = rawCandles.slice(i, i + groupSize);
      if (chunk.length === 0) continue;
      const first = chunk[0];
      const last = chunk[chunk.length - 1];
      let high = -Infinity;
      let low = Infinity;
      let totalVol = 0;
      for (const c of chunk) {
        if (c.high > high) high = c.high;
        if (c.low < low) low = c.low;
        totalVol += (c.volume || 0);
      }
      aggregated.push({
        time: first.time,
        open: first.open,
        high: high,
        low: low,
        close: last.close,
        volume: totalVol
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

  setData(symbol, candles, currentPrice) {
    this.symbol = symbol;
    this.rawCandles = candles || [];
    this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    this.currentPrice = currentPrice || (this.candles.length ? this.candles[this.candles.length - 1].close : 0);
    this.panOffset = 0;
    this.render();
  }

  updateLiveTick(price, size) {
    if (!price || isNaN(price)) return;
    this.currentPrice = price;
    if (this.rawCandles && this.rawCandles.length > 0) {
      const last = this.rawCandles[this.rawCandles.length - 1];
      // Defensive outlier guard: prevent mismatched cross-asset ticks from distorting the candle
      const refPrice = last.close || last.open;
      if (refPrice > 0 && Math.abs(price - refPrice) / refPrice > 0.35) {
        return;
      }
      last.high = Math.max(last.high, price);
      last.low = Math.min(last.low, price);
      last.close = price;
      last.volume += (size || 0);
      this.candles = this.aggregateCandles(this.rawCandles, this.interval);
    } else if (this.candles.length > 0) {
      const last = this.candles[this.candles.length - 1];
      last.high = Math.max(last.high, price);
      last.low = Math.min(last.low, price);
      last.close = price;
      last.volume += (size || 0);
    }
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
    const plotHeight = this.height - marginBottom - marginTop;

    // Calculate High / Low range
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVol = 0;

    for (const c of this.candles) {
      if (c.low < minPrice) minPrice = c.low;
      if (c.high > maxPrice) maxPrice = c.high;
      if (c.volume > maxVol) maxVol = c.volume;
    }

    if (this.currentPrice > 0) {
      minPrice = Math.min(minPrice, this.currentPrice);
      maxPrice = Math.max(maxPrice, this.currentPrice);
    }

    // Padding (5% headroom and footroom)
    const range = (maxPrice - minPrice) || 1.0;
    minPrice -= range * 0.05;
    maxPrice += range * 0.05;

    const priceToY = (p) => marginTop + plotHeight - ((p - minPrice) / (maxPrice - minPrice)) * plotHeight;
    const yToPrice = (y) => maxPrice - ((y - marginTop) / plotHeight) * (maxPrice - minPrice);

    // Draw Grid Lines & Price Axis
    ctx.strokeStyle = '#1e1a0d';
    ctx.lineWidth = 1;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#996a00';

    const gridSteps = 5;
    for (let i = 0; i <= gridSteps; i++) {
      const y = marginTop + (plotHeight / gridSteps) * i;
      const p = maxPrice - ((maxPrice - minPrice) / gridSteps) * i;

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(plotWidth, y);
      ctx.stroke();

      ctx.fillText(p.toFixed(2), plotWidth + 6, y + 3);
    }

    // Calculate dynamic candle width with zoom and pan
    const baseCandleWidth = Math.max(2, Math.floor(plotWidth / (this.candles.length * 1.5)));
    const candleWidth = Math.min(32, Math.max(3, Math.floor(baseCandleWidth * this.zoomLevel)));
    const gap = Math.max(1, Math.floor(candleWidth * 0.4));
    const totalCandleSpan = candleWidth + gap;

    // Bounded pan offset and right-alignment
    const totalContentWidth = this.candles.length * totalCandleSpan;
    const rightAlignOffset = (totalContentWidth < plotWidth) ? (plotWidth - totalContentWidth - 15) : 10;
    const minPan = Math.min(0, plotWidth - totalContentWidth - 20);
    const maxPan = 20;
    this.panOffset = Math.max(minPan, Math.min(maxPan, this.panOffset));

    let hoveredCandle = null;
    let hoveredX = -1;

    // Draw Candles & Volume Bars
    for (let i = 0; i < this.candles.length; i++) {
      const c = this.candles[i];
      const x = rightAlignOffset + i * totalCandleSpan + this.panOffset;
      if (x + candleWidth < 0 || x > plotWidth) continue;

      const isUp = c.close >= c.open;

      // Volume bar at bottom
      const volHeight = maxVol > 0 ? (c.volume / maxVol) * (plotHeight * 0.22) : 0;
      ctx.fillStyle = isUp ? 'rgba(0, 255, 102, 0.2)' : 'rgba(255, 51, 68, 0.2)';
      ctx.fillRect(x, marginTop + plotHeight - volHeight, candleWidth, volHeight);

      // Candlestick Wick
      ctx.strokeStyle = isUp ? '#00ff66' : '#ff3344';
      ctx.beginPath();
      ctx.moveTo(x + candleWidth / 2, priceToY(c.high));
      ctx.lineTo(x + candleWidth / 2, priceToY(c.low));
      ctx.stroke();

      // Candlestick Body
      const yOpen = priceToY(c.open);
      const yClose = priceToY(c.close);
      const bodyY = Math.min(yOpen, yClose);
      const bodyH = Math.max(Math.abs(yClose - yOpen), 1);

      ctx.fillStyle = isUp ? '#00ff66' : '#ff3344';
      ctx.fillRect(x, bodyY, candleWidth, bodyH);

      // Check mouse hover
      if (this.mouse.active && this.mouse.x >= x - gap / 2 && this.mouse.x <= x + candleWidth + gap / 2) {
        hoveredCandle = c;
        hoveredX = x + candleWidth / 2;
      }
    }

    // Current Price Dashed Reference Line
    if (this.currentPrice > 0) {
      const liveY = priceToY(this.currentPrice);
      if (liveY >= marginTop && liveY <= marginTop + plotHeight) {
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
        ctx.fillText(this.currentPrice.toFixed(2), plotWidth + 4, liveY + 4);
      }
    }

    // Interactive Crosshair & Tooltip HUD
    if (this.mouse.active && this.mouse.x <= plotWidth && this.mouse.y >= marginTop && this.mouse.y <= marginTop + plotHeight) {
      const crossX = hoveredX > 0 ? hoveredX : this.mouse.x;
      const crossY = this.mouse.y;

      // Crosshair lines
      ctx.strokeStyle = 'rgba(255, 176, 0, 0.45)';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);

      // Vertical line
      ctx.beginPath();
      ctx.moveTo(crossX, marginTop);
      ctx.lineTo(crossX, marginTop + plotHeight);
      ctx.stroke();

      // Horizontal line
      ctx.beginPath();
      ctx.moveTo(0, crossY);
      ctx.lineTo(plotWidth, crossY);
      ctx.stroke();
      ctx.setLineDash([]);

      // Price indicator on Y-axis
      const hoverPrice = yToPrice(crossY);
      ctx.fillStyle = '#ffcc00';
      ctx.fillRect(plotWidth, crossY - 8, marginRight, 16);
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 9px monospace';
      ctx.fillText(hoverPrice.toFixed(2), plotWidth + 4, crossY + 4);

      // Top HUD Bar showing candle metrics
      if (hoveredCandle) {
        const c = hoveredCandle;
        const chg = c.close - c.open;
        const chgPct = (chg / c.open) * 100;
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
        ctx.fillText(c.open.toFixed(2), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('H:', tx, 16); tx += 15;
        ctx.fillStyle = '#00ff66';
        ctx.fillText(c.high.toFixed(2), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('L:', tx, 16); tx += 15;
        ctx.fillStyle = '#ff3344';
        ctx.fillText(c.low.toFixed(2), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('C:', tx, 16); tx += 15;
        ctx.fillStyle = '#fff';
        ctx.fillText(c.close.toFixed(2), tx, 16); tx += 55;

        ctx.fillStyle = '#888';
        ctx.fillText('CHG:', tx, 16); tx += 28;
        ctx.fillStyle = chgColor;
        ctx.fillText(`${sign}${chg.toFixed(2)} (${sign}${chgPct.toFixed(2)}%)`, tx, 16); tx += 95;

        ctx.fillStyle = '#888';
        ctx.fillText('VOL:', tx, 16); tx += 28;
        ctx.fillStyle = '#ffcc00';
        ctx.fillText(Math.round(c.volume).toLocaleString(), tx, 16);
      }
    } else {
      // Default top info bar when not hovering
      ctx.fillStyle = '#111111';
      ctx.fillRect(0, 0, plotWidth, marginTop);
      ctx.strokeStyle = '#222';
      ctx.strokeRect(0, 0, plotWidth, marginTop);

      ctx.font = 'bold 11px monospace';
      ctx.fillStyle = '#ffb000';
      ctx.fillText(`${this.symbol} [${this.interval}] INTRADAY CANDLESTICK ACTION (60 FPS)`, 8, 16);

      ctx.font = '10px monospace';
      ctx.fillStyle = '#888';
      ctx.fillText('DOUBLE-CLICK TO RESET ZOOM / DRAG TO PAN', plotWidth - 250, 16);
    }
  }
}

window.PriceChart = PriceChart;
