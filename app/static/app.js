const form = document.getElementById("analyzeForm");
const queryInput = document.getElementById("queryInput");
const submitBtn = document.getElementById("submitBtn");
const errorBox = document.getElementById("errorBox");

const modeChip = document.getElementById("modeChip");
const freshnessChip = document.getElementById("freshnessChip");
const timeChip = document.getElementById("timeChip");

const baseSummary = document.getElementById("baseSummary");
const revisedSummary = document.getElementById("revisedSummary");
const baseItems = document.getElementById("baseItems");
const revisedItems = document.getElementById("revisedItems");
const updatesList = document.getElementById("updatesList");
const diffList = document.getElementById("diffList");
const reverseBtn = document.getElementById("reverseBtn");
const reverseOutput = document.getElementById("reverseOutput");

let latestItemName = "";

function setBusy(busy) {
  submitBtn.disabled = busy;
  submitBtn.textContent = busy ? "校准中..." : "开始校准";
}

function setError(message) {
  if (!message) {
    errorBox.hidden = true;
    errorBox.textContent = "";
    return;
  }
  errorBox.hidden = false;
  errorBox.textContent = message;
}

function renderItems(target, items) {
  target.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.className = "hint";
    li.textContent = "暂无数据";
    target.appendChild(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="name">${item.name}</span> · ${item.price_text}<br><span class="hint">${item.reason}</span>`;
    target.appendChild(li);
  }
}

function renderSimpleList(target, lines) {
  target.innerHTML = "";
  if (!lines || lines.length === 0) {
    const li = document.createElement("li");
    li.className = "hint";
    li.textContent = "暂无变化";
    target.appendChild(li);
    return;
  }
  for (const line of lines) {
    const li = document.createElement("li");
    li.innerHTML = line;
    target.appendChild(li);
  }
}

function freshnessLabel(level) {
  if (level === "high") return "高";
  if (level === "medium") return "中";
  if (level === "low") return "低";
  return "-";
}

function setReverseState(itemName) {
  latestItemName = itemName || "";
  reverseBtn.disabled = !latestItemName;
}

function renderReverse(text) {
  reverseOutput.hidden = false;
  reverseOutput.innerHTML = `<strong>品牌方视角：</strong><br>${text}`;
}

async function analyze(query) {
  const url = `/analyze?query=${encodeURIComponent(query)}`;
  const resp = await fetch(url, { method: "GET" });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`请求失败 (${resp.status}) ${body}`);
  }
  return await resp.json();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) return;

  setError("");
  setBusy(true);
  try {
    const data = await analyze(query);
    const mode = data.web_updates.length ? "联网校准" : "基础推荐有效";
    modeChip.textContent = `模式：${mode}`;
    freshnessChip.textContent = `新鲜度：${freshnessLabel(data.freshness.level)} (${data.freshness.score})`;
    timeChip.textContent = `时间：${new Date(data.generated_at).toLocaleString()}`;

    baseSummary.textContent = data.base_recommendation.summary;
    revisedSummary.textContent = data.revised_recommendation.summary;

    renderItems(baseItems, data.base_recommendation.items);
    renderItems(revisedItems, data.revised_recommendation.items);
    setReverseState(
      data.revised_recommendation.items[0]?.name || data.base_recommendation.items[0]?.name || ""
    );

    const updates = data.web_updates.map(
      (u) =>
        `<strong>${u.item_name}</strong> [${u.update_type}] ${u.update_text}<br><span class="hint">${u.source_title} · ${u.published_at}</span>`
    );
    renderSimpleList(updatesList, updates);

    const diffs = data.diff_points.map(
      (d) =>
        `<strong>${d.field}</strong>: ${d.before} → ${d.after}<br><span class="hint">${d.reason}</span>`
    );
    renderSimpleList(diffList, diffs);
  } catch (err) {
    setError(err instanceof Error ? err.message : "请求失败");
  } finally {
    setBusy(false);
  }
});

reverseBtn.addEventListener("click", async () => {
  if (!latestItemName) return;

  setError("");
  reverseBtn.disabled = true;
  reverseBtn.textContent = "生成中...";
  try {
    const resp = await fetch(`/reverse?item_name=${encodeURIComponent(latestItemName)}`, {
      method: "GET",
    });
    if (!resp.ok) {
      const body = await resp.text();
      throw new Error(`请求失败 (${resp.status}) ${body}`);
    }
    const data = await resp.json();
    renderReverse(data.reverse_text);
  } catch (err) {
    setError(err instanceof Error ? err.message : "请求失败");
  } finally {
    reverseBtn.textContent = "查看品牌方怎么说";
    reverseBtn.disabled = !latestItemName;
  }
});
