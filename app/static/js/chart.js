/*
 * PD3board Hardware-Accelerated 60 FPS HTML5 Canvas Financial Chart
 */

class PriceChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!canvasId || !this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.candles = [];
    this.currentPrice = 0;
    this.symbol = 'BTCUSDT';
    
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
    this.render();
  }

  setData(symbol, candles, currentPrice) {
    this.symbol = symbol;
    this.candles = candles || [];
    this.currentPrice = currentPrice || (this.candles.length ? this.candles[this.candles.length - 1].close : 0);
    this.render();
  }

  updateLiveTick(price, size) {
    this.currentPrice = price;
    if (this.candles.length > 0) {
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

    // Background
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, this.width, this.height);

    if (this.candles.length === 0) {
      ctx.fillStyle = '#666';
      ctx.font = '12px monospace';
      ctx.fillText('Awaiting real-time tick stream for ' + this.symbol + '...', 20, 30);
      return;
    }

    // Chart margins
    const marginRight = 65;
    const marginBottom = 25;
    const plotWidth = this.width - marginRight;
    const plotHeight = this.height - marginBottom;

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

    // Padding
    const range = (maxPrice - minPrice) || 1.0;
    minPrice -= range * 0.05;
    maxPrice += range * 0.05;

    const priceToY = (p) => plotHeight - ((p - minPrice) / (maxPrice - minPrice)) * plotHeight;

    // Draw Grid Lines & Price Axis
    ctx.strokeStyle = '#1e1a0d';
    ctx.lineWidth = 1;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#996a00';

    const gridSteps = 6;
    for (let i = 0; i <= gridSteps; i++) {
      const y = (plotHeight / gridSteps) * i;
      const p = maxPrice - ((maxPrice - minPrice) / gridSteps) * i;

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(plotWidth, y);
      ctx.stroke();

      ctx.fillText(p.toFixed(2), plotWidth + 6, y + 3);
    }

    // Draw Candles & Volume Bars
    const candleWidth = Math.max(2, Math.floor(plotWidth / (this.candles.length * 1.5)));
    const gap = candleWidth * 0.5;

    for (let i = 0; i < this.candles.length; i++) {
      const c = this.candles[i];
      const x = i * (candleWidth + gap) + 10;
      const isUp = c.close >= c.open;

      // Volume bar
      const volHeight = maxVol > 0 ? (c.volume / maxVol) * (plotHeight * 0.2) : 0;
      ctx.fillStyle = isUp ? 'rgba(0, 255, 102, 0.2)' : 'rgba(255, 51, 68, 0.2)';
      ctx.fillRect(x, plotHeight - volHeight, candleWidth, volHeight);

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
    }

    // Current Price Line
    if (this.currentPrice > 0) {
      const liveY = priceToY(this.currentPrice);
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
}

window.PriceChart = PriceChart;
