import type { LogRow, TraderDetail } from "./api";
import { getTrader, getTraderLogs } from "./api";
import { PortfolioChart } from "./chart";
import { LogView } from "./log";
import { TransactionsView } from "./transactions";

interface ChartPoint {
  t: number;
  value: number;
}

function toUnixSeconds(stamp: string): number {
  return new Date(stamp.replace(" ", "T")).getTime() / 1000;
}

const MODAL_LOG_LIMIT = 500;

let currentModal: HTMLElement | null = null;

function buildModalContent(name: string, detail: TraderDetail, logs: LogRow[]): HTMLElement {
  const card = document.createElement("div");
  card.className = "modal-card";

  card.innerHTML = `
    <div class="modal-header">
      <span class="modal-trader-name">${name}</span>
      <span class="modal-trader-sub">${detail.model_name} · ${detail.lastname}</span>
      <button class="modal-close" aria-label="Close modal">&times;</button>
    </div>
    <div class="modal-body">
      <div class="modal-chart"></div>
      <div class="modal-bottom">
        <div class="modal-col">
          <span class="modal-col-label">Activity log</span>
          <div class="modal-log"></div>
        </div>
        <div class="modal-col">
          <span class="modal-col-label">All trades</span>
          <div class="modal-txns"></div>
        </div>
      </div>
    </div>
  `;

  const chartHost = card.querySelector(".modal-chart") as HTMLElement;
  const logHost = card.querySelector(".modal-log") as HTMLElement;
  const txnHost = card.querySelector(".modal-txns") as HTMLElement;

  const chart = new PortfolioChart(chartHost);
  const points: ChartPoint[] = detail.time_series.map((p) => ({
    t: toUnixSeconds(p.datetime),
    value: p.value,
  }));
  chart.update(points);

  const logView = new LogView(logHost);
  logView.render(logs);

  const txnView = new TransactionsView(txnHost, 500);
  txnView.render(detail.transactions);

  card.querySelector(".modal-close")!.addEventListener("click", closeTraderModal);

  return card;
}

export function openTraderModal(name: string): void {
  const root = document.getElementById("modal-root");
  if (!root) return;

  if (currentModal) {
    closeTraderModal();
  }

  const backdrop = document.createElement("div");
  backdrop.className = "modal-backdrop";
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) closeTraderModal();
  });

  const loading = document.createElement("div");
  loading.className = "modal-card modal-loading";
  loading.textContent = "Loading...";
  backdrop.append(loading);
  root.append(backdrop);
  root.classList.add("open");

  Promise.all([getTrader(name), getTraderLogs(name, MODAL_LOG_LIMIT)])
    .then(([detail, logs]) => {
      const card = buildModalContent(name, detail, logs);
      backdrop.innerHTML = "";
      backdrop.append(card);
    })
    .catch((err) => {
      backdrop.innerHTML = `<div class="modal-card modal-loading">Failed to load: ${err.message}</div>`;
    });

  currentModal = backdrop;
}

export function closeTraderModal(): void {
  const root = document.getElementById("modal-root");
  if (root) {
    root.classList.remove("open");
    root.innerHTML = "";
  }
  currentModal = null;
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeTraderModal();
});
