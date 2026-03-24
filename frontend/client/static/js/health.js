document.addEventListener("DOMContentLoaded", () => {
  const card = document.getElementById("health-card");
  if (!card) return;
  const statusEl = document.getElementById("health-status");
  const uptimeEl = document.getElementById("health-uptime");
  const btn = document.getElementById("health-refresh");

  const container = card.closest("[data-uaa-url]");
  const baseUrl = container ? container.dataset.uaaUrl || "" : "";
  const statusUrl = baseUrl.replace(/\/+$/, "") + "/status";

  async function refresh() {
    try {
      statusEl.textContent = "Loading...";
      const res = await fetch(statusUrl, { credentials: "include" });
      const data = await res.json();
      statusEl.textContent = data.status || res.status;
      const up = ((data.data || {}).uptime_seconds) || 0;
      const mins = Math.floor(up / 60);
      uptimeEl.textContent = `${mins}m ${up % 60}s`;
    } catch (e) {
      statusEl.textContent = "Error";
      uptimeEl.textContent = "-";
    }
  }

  btn && btn.addEventListener("click", refresh);
  refresh();
});
