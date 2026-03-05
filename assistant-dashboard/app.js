const STORAGE_KEY = "assistant_dashboard_v2";

const statuses = ["todo", "doing", "done"];
const labels = { todo: "To Do", doing: "In Progress", done: "Done" };

const defaultData = {
  tasks: [
    {
      id: crypto.randomUUID(),
      title: "Luxury landing page for Mr & Ms PauleauZ",
      details: "Built and delivered with all extracted property listings.",
      status: "done",
      priority: "high",
      owner: "Assistant",
      dueDate: "",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: crypto.randomUUID(),
      title: "Upgrade assistant dashboard",
      details: "Improve UX, filtering, metrics, and reliability checks.",
      status: "doing",
      priority: "high",
      owner: "Assistant",
      dueDate: "",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
  ],
  updates: [
    {
      id: crypto.randomUUID(),
      text: "Dashboard initialized and ready for live tracking.",
      at: new Date().toISOString()
    }
  ]
};

const dom = {
  metrics: document.getElementById("metrics"),
  board: document.getElementById("board"),
  updates: document.getElementById("updates"),
  taskCounter: document.getElementById("taskCounter"),
  progressText: document.getElementById("progressText"),
  progressFill: document.getElementById("progressFill"),
  searchInput: document.getElementById("searchInput"),
  priorityFilter: document.getElementById("priorityFilter"),
  ownerFilter: document.getElementById("ownerFilter"),
  addTaskBtn: document.getElementById("addTaskBtn"),
  addUpdateBtn: document.getElementById("addUpdateBtn"),
  clearDoneBtn: document.getElementById("clearDoneBtn"),
  exportBtn: document.getElementById("exportBtn"),
  importFile: document.getElementById("importFile"),
  taskTemplate: document.getElementById("taskTemplate")
};

function clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function load() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultData));
    return clone(defaultData);
  }
  try {
    const parsed = JSON.parse(raw);
    parsed.tasks = Array.isArray(parsed.tasks) ? parsed.tasks : [];
    parsed.updates = Array.isArray(parsed.updates) ? parsed.updates : [];
    return parsed;
  } catch {
    return clone(defaultData);
  }
}

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function now() {
  return new Date().toISOString();
}

function addUpdate(text) {
  data.updates.push({ id: crypto.randomUUID(), text, at: now() });
  if (data.updates.length > 200) data.updates = data.updates.slice(-200);
}

function normalized(text) {
  return String(text || "").toLowerCase();
}

function isOverdue(task) {
  if (!task.dueDate || task.status === "done") return false;
  const due = new Date(task.dueDate + "T23:59:59");
  return due.getTime() < Date.now();
}

function getFilteredTasks() {
  const q = normalized(dom.searchInput.value.trim());
  const priority = dom.priorityFilter.value;
  const owner = dom.ownerFilter.value;

  return data.tasks.filter(task => {
    const matchesQ = !q || [task.title, task.details, task.owner].some(v => normalized(v).includes(q));
    const matchesPriority = priority === "all" || task.priority === priority;
    const matchesOwner = owner === "all" || task.owner === owner;
    return matchesQ && matchesPriority && matchesOwner;
  });
}

function renderMetrics(filteredTasks) {
  const total = data.tasks.length;
  const done = data.tasks.filter(t => t.status === "done").length;
  const doing = data.tasks.filter(t => t.status === "doing").length;
  const overdue = data.tasks.filter(isOverdue).length;
  const completion = total ? Math.round((done / total) * 100) : 0;

  const cards = [
    ["Total Tasks", total],
    ["Completion", `${completion}%`],
    ["In Progress", doing],
    ["Overdue", overdue],
    ["Visible (filtered)", filteredTasks.length]
  ];

  dom.metrics.innerHTML = cards
    .map(([name, value]) => `<article class="card"><h3>${name}</h3><strong>${value}</strong></article>`)
    .join("");

  dom.progressText.textContent = `${completion}%`;
  dom.progressFill.style.width = `${completion}%`;
  dom.taskCounter.textContent = `${filteredTasks.length} tasks`;
}

function priorityRank(priority) {
  return { high: 0, medium: 1, low: 2 }[priority] ?? 3;
}

function formatTaskMeta(task) {
  const due = task.dueDate ? `Due: ${task.dueDate}` : "No due date";
  const overdue = isOverdue(task) ? " · OVERDUE" : "";
  return `Owner: ${task.owner} · ${due}${overdue} · Updated: ${new Date(task.updatedAt).toLocaleString()}`;
}

function nextStatus(current) {
  const idx = statuses.indexOf(current);
  return statuses[(idx + 1) % statuses.length];
}

function renderBoard(filteredTasks) {
  dom.board.innerHTML = "";

  statuses.forEach(status => {
    const column = document.createElement("div");
    column.className = "column";
    column.innerHTML = `<h3>${labels[status]}</h3>`;

    filteredTasks
      .filter(t => t.status === status)
      .sort((a, b) => priorityRank(a.priority) - priorityRank(b.priority))
      .forEach(task => {
        const node = dom.taskTemplate.content.firstElementChild.cloneNode(true);
        node.querySelector("h4").textContent = task.title;
        node.querySelector(".details").textContent = task.details || "No details";

        const badge = node.querySelector(".badge");
        badge.textContent = task.priority.toUpperCase();
        badge.classList.add(task.priority);

        node.querySelector(".meta").textContent = formatTaskMeta(task);

        node.querySelector(".move").addEventListener("click", () => {
          task.status = nextStatus(task.status);
          task.updatedAt = now();
          addUpdate(`Task moved to ${labels[task.status]}: ${task.title}`);
          save();
          render();
        });

        node.querySelector(".edit").addEventListener("click", () => {
          editTask(task);
        });

        node.querySelector(".delete").addEventListener("click", () => {
          if (!confirm(`Delete task: ${task.title}?`)) return;
          data.tasks = data.tasks.filter(t => t.id !== task.id);
          addUpdate(`Task deleted: ${task.title}`);
          save();
          render();
        });

        column.appendChild(node);
      });

    dom.board.appendChild(column);
  });
}

function renderUpdates() {
  const html = [...data.updates]
    .sort((a, b) => b.at.localeCompare(a.at))
    .map(item => `<li><p>${item.text}</p><time>${new Date(item.at).toLocaleString()}</time></li>`)
    .join("");

  dom.updates.innerHTML = html || "<li><p>No updates yet.</p></li>";
}

function promptTask(initial = {}) {
  const title = prompt("Task title:", initial.title || "");
  if (!title) return null;

  const details = prompt("Task details:", initial.details || "") || "";
  const priority = (prompt("Priority (high/medium/low):", initial.priority || "medium") || "medium").toLowerCase();
  const owner = prompt("Owner (Assistant/Marcus):", initial.owner || "Assistant") || "Assistant";
  const dueDate = prompt("Due date (YYYY-MM-DD) or leave blank:", initial.dueDate || "") || "";

  const cleanPriority = ["high", "medium", "low"].includes(priority) ? priority : "medium";
  const cleanOwner = owner === "Marcus" ? "Marcus" : "Assistant";

  return { title: title.trim(), details: details.trim(), priority: cleanPriority, owner: cleanOwner, dueDate: dueDate.trim() };
}

function editTask(task) {
  const updated = promptTask(task);
  if (!updated) return;
  Object.assign(task, updated, { updatedAt: now() });
  addUpdate(`Task edited: ${task.title}`);
  save();
  render();
}

function addTask() {
  const task = promptTask();
  if (!task) return;

  data.tasks.push({
    id: crypto.randomUUID(),
    ...task,
    status: "todo",
    createdAt: now(),
    updatedAt: now()
  });

  addUpdate(`Task created: ${task.title}`);
  save();
  render();
}

function addManualUpdate() {
  const text = prompt("Update note:");
  if (!text) return;
  addUpdate(text.trim());
  save();
  render();
}

function clearDone() {
  const doneCount = data.tasks.filter(t => t.status === "done").length;
  if (!doneCount) return alert("No done tasks to clear.");
  if (!confirm(`Clear ${doneCount} completed task(s)?`)) return;

  data.tasks = data.tasks.filter(t => t.status !== "done");
  addUpdate(`Cleared ${doneCount} completed task(s).`);
  save();
  render();
}

function exportJson() {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `assistant-dashboard-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function importJson(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const parsed = JSON.parse(reader.result);
      if (!Array.isArray(parsed.tasks) || !Array.isArray(parsed.updates)) throw new Error("Invalid structure");
      data = parsed;
      addUpdate("Imported dashboard data from JSON file.");
      save();
      render();
      alert("Import successful.");
    } catch {
      alert("Import failed: invalid JSON format.");
    }
  };
  reader.readAsText(file);
}

function bind() {
  [dom.searchInput, dom.priorityFilter, dom.ownerFilter].forEach(el => el.addEventListener("input", render));
  dom.addTaskBtn.addEventListener("click", addTask);
  dom.addUpdateBtn.addEventListener("click", addManualUpdate);
  dom.clearDoneBtn.addEventListener("click", clearDone);
  dom.exportBtn.addEventListener("click", exportJson);
  dom.importFile.addEventListener("change", e => {
    const file = e.target.files?.[0];
    if (file) importJson(file);
    e.target.value = "";
  });
}

function render() {
  const filteredTasks = getFilteredTasks();
  renderMetrics(filteredTasks);
  renderBoard(filteredTasks);
  renderUpdates();
}

let data = load();
bind();
render();
