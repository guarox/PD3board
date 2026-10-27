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

    topBids.forEach(b => { if (Number(b.total || 0) > maxTotal) maxTotal = Number(b.total || 0); });
    topAsks.forEach(a => { if (Number(a.total || 0) > maxTotal) maxTotal = Number(a.total || 0); });

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
      const pct = Math.min((Number(a.total || 0) / maxTotal) * 100, 100) || 0;
      html += `
        <div class="depth-row">
          <div class="depth-bar depth-bar-ask" style="width: ${pct}%"></div>
          <div class="neg">${Number(a.size || 0).toFixed(4)}</div>
          <div class="text-center neg">${Number(a.price || 0).toFixed(2)}</div>
          <div class="text-right neu">${Number(a.total || 0).toFixed(4)}</div>
        </div>
      `;
    });

    // Spread Row
    html += `
      <div class="spread-row">
        <span>SPREAD: ${Number(spread || 0).toFixed(2)} (${Number(spread_bps || 0).toFixed(1)} BPS)</span>
      </div>
      <div class="bids-container">
    `;

    // Render Bids
    topBids.forEach(b => {
      const pct = Math.min((Number(b.total || 0) / maxTotal) * 100, 100) || 0;
      html += `
        <div class="depth-row">
          <div class="depth-bar depth-bar-bid" style="width: ${pct}%"></div>
          <div class="pos">${Number(b.size || 0).toFixed(4)}</div>
          <div class="text-center pos">${Number(b.price || 0).toFixed(2)}</div>
          <div class="text-right neu">${Number(b.total || 0).toFixed(4)}</div>
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
