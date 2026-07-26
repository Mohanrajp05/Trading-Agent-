// A trader's recent trades, newest first. Mirrors the activity log's compact style.

import type { Transaction } from "./api";

export class TransactionsView {
  private host: HTMLElement;
  private maxRows: number;

  constructor(host: HTMLElement, maxRows = 12) {
    this.host = host;
    this.maxRows = maxRows;
    host.classList.add("txns");
  }

  render(transactions: Transaction[]): void {
    this.host.innerHTML = "";
    if (transactions.length === 0) {
      const empty = document.createElement("div");
      empty.className = "txn-empty";
      empty.textContent = "No trades yet";
      this.host.append(empty);
      return;
    }
    for (const t of transactions.slice(-this.maxRows).reverse()) {
      const row = document.createElement("div");
      row.className = "txn-row";

      const date = document.createElement("span");
      date.className = "txn-date";
      date.textContent = dateOf(t.timestamp);

      const side = document.createElement("span");
      side.className = "txn-side";
      side.dataset.side = t.quantity >= 0 ? "buy" : "sell";
      side.textContent = t.quantity >= 0 ? "BUY" : "SELL";

      const detail = document.createElement("span");
      detail.className = "txn-detail";
      detail.textContent = `${Math.abs(t.quantity)} ${t.symbol} @ $${t.price.toFixed(2)}`;

      row.append(date, side, detail);
      this.host.append(row);
    }
  }
}

function dateOf(stamp: string): string {
  // "YYYY-MM-DD HH:MM:SS" -> "MM-DD"
  const parts = stamp.split(" ")[0].split("-");
  return parts.length === 3 ? `${parts[1]}-${parts[2]}` : stamp;
}
