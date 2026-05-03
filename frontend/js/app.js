let tokensGlobal = [];
let currentIndex = 0;

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function syncLineNumbers() {
  const ta = document.getElementById("code-input");
  const gutter = document.getElementById("line-numbers");
  if (!ta || !gutter) return;

  const lines = ta.value.split("\n").length || 1;
  const nums = Array.from({ length: lines }, (_, i) => String(i + 1)).join(
    "\n",
  );
  gutter.textContent = nums;
  gutter.style.minHeight = ta.scrollHeight + "px";
  gutter.style.transform = `translateY(-${ta.scrollTop}px)`;
}

function appendTokenRow(token) {
  const output = document.getElementById("token-output");
  if (!output) return;

  const row = document.createElement("div");
  row.className = "token-line";
  row.innerHTML =
    '&lt;<span class="token-lexema">\'' +
    escapeHtml(token.lexema) +
    '\'</span>, <span class="token-type">' +
    escapeHtml(token.tipo) +
    "</span>&gt;";
  output.appendChild(row);
  output.scrollTop = output.scrollHeight;
}

document.getElementById("btn-analyze")?.addEventListener("click", analizarTodo);

document
  .getElementById("code-input")
  ?.addEventListener("input", syncLineNumbers);
document.getElementById("code-input")?.addEventListener("scroll", function () {
  const gutter = document.getElementById("line-numbers");
  if (gutter) gutter.style.transform = `translateY(-${this.scrollTop}px)`;
});

document
  .getElementById("btn-copy-tokens")
  ?.addEventListener("click", async () => {
    const el = document.getElementById("token-output");
    if (!el) return;
    const text = Array.from(el.querySelectorAll(".token-line"))
      .map((row) => row.textContent.trim())
      .join("\n");
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      /* ignore */
    }
  });

syncLineNumbers();

async function analizarTodo() {
  const codigo = document.getElementById("code-input").value;
  const treeArea = document.getElementById("tree-area");

  setTreeMessage("Analizando...");

  const response = await fetch("http://127.0.0.1:5000/api/analizar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo }),
  });

  if (!response.ok) {
    setTreeMessage("Error de conexión con el servidor.");
    return;
  }

  const data = await response.json();
  tokensGlobal = data.tokens || [];
  currentIndex = 0;

  const output = document.getElementById("token-output");
  if (output) output.innerHTML = "";

  for (const token of tokensGlobal) {
    appendTokenRow(token);
  }
  currentIndex = tokensGlobal.length;
  actualizarProgreso();

  if (data.parserError) {
    setTreeMessage(`Error sintáctico: ${escapeHtml(data.parserError)}`);
    return;
  }

  if (!data.tree) {
    setTreeMessage("No se generó ningún árbol sintáctico.");
    return;
  }

  if (treeArea) {
    treeArea.innerHTML = "";
    treeArea.appendChild(renderTreeNode(data.tree));
  }
}

function setTreeMessage(message) {
  const treeArea = document.getElementById("tree-area");
  if (!treeArea) return;
  treeArea.innerHTML = "";
  const msg = document.createElement("div");
  msg.className = "tree-message";
  msg.textContent = message;
  treeArea.appendChild(msg);
}

function renderTreeNode(node) {
  const nodeWrapper = document.createElement("div");
  nodeWrapper.className = "tree-container";

  const nodeCard = document.createElement("div");
  nodeCard.className = `tree-node${node.type === "Program" ? " tree-node--root" : ""}`;

  const label = document.createElement("div");
  label.className = "tree-node__label";
  label.textContent = node.label || node.type;

  const typeLabel = document.createElement("div");
  typeLabel.className = "tree-node__type";
  typeLabel.textContent = node.type;

  nodeCard.appendChild(label);
  nodeCard.appendChild(typeLabel);
  nodeWrapper.appendChild(nodeCard);

  if (node.children && node.children.length > 0) {
    const childContainer = document.createElement("div");
    childContainer.className = "tree-children";
    for (const child of node.children) {
      childContainer.appendChild(renderTreeNode(child));
    }
    nodeWrapper.appendChild(childContainer);
  }

  return nodeWrapper;
}

function actualizarProgreso() {
  const n = tokensGlobal.length;
  const percent = n === 0 ? 0 : Math.round((currentIndex / n) * 100);
  const fill = document.getElementById("progress-fill");
  const label = document.getElementById("progress-percent");
  if (fill) fill.style.width = percent + "%";
  if (label) label.textContent = percent + "%";
}
