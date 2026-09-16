/*
 * PD3board Level 2 Order Book Ladder & Depth Renderer
 */

class OrderBookUI {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.maxLevels = 10;
  }

  update(depthData) {
    if (!this.container || !depthData) return;
    const { bids, asks, best_bid, best_ask, spread, spread_bps, symbol } = depthData;

    let maxTotal = 1.0;
    const topBids = (bids || []).slice(0, this.maxLevels);
    const topAsks = (asks || []).slice(0, this.maxLevels);

    topBids.forEach(b => { if (b.total > maxTotal) maxTotal = b.total; });
    topAsks.forEach(a => { if (a.total > maxTotal) maxTotal = a.total; });

    let html = `
      <div class="depth-ladder">
        <div class="depth-header">
          <div>SIZE</div>
          <div class="text-center">PRICE</div>
          <div class="text-right">TOTAL</div>
        </div>
        <div class="asks-container">
    `;

    // Render Asks (reversed so lowest ask is adjacent to spread)
    const reversedAsks = [...topAsks].reverse();
    reversedAsks.forEach(a => {
      const pct = Math.min((a.total / maxTotal) * 100, 100);
      html += `
        <div class="depth-row">
          <div class="depth-bar depth-bar-ask" style="width: ${pct}%"></div>
          <div class="neg">${a.size.toFixed(4)}</div>
          <div class="text-center neg">${a.price.toFixed(2)}</div>
          <div class="text-right neu">${a.total.toFixed(4)}</div>
        </div>
      `;
    });

    // Spread Row
    html += `
      <div class="spread-row">
        <span>SPREAD: ${spread.toFixed(2)} (${spread_bps.toFixed(1)} BPS)</span>
      </div>
      <div class="bids-container">
    `;

    // Render Bids
    topBids.forEach(b => {
      const pct = Math.min((b.total / maxTotal) * 100, 100);
      html += `
        <div class="depth-row">
          <div class="depth-bar depth-bar-bid" style="width: ${pct}%"></div>
          <div class="pos">${b.size.toFixed(4)}</div>
          <div class="text-center pos">${b.price.toFixed(2)}</div>
          <div class="text-right neu">${b.total.toFixed(4)}</div>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;

    this.container.innerHTML = html;
  }
}

window.OrderBookUI = OrderBookUI;
