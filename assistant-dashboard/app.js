const STORAGE_KEY = "assistant_dashboard_v1";

const defaultData = {
  tasks: [
    {
      id: crypto.randomUUID(),
      title: "Luxury landing page for Mr & Ms PauleauZ",
      details: "Built and delivered with all extracted property listings.",
      status: "done",
      updatedAt: new Date().toISOString()
    },
    {
      id: crypto.randomUUID(),
      title: "Performance dashboard setup",
      details: "Create dashboard to track tasks and updates.",
      status: "doing",
      updatedAt: new Date().toISOString()
    }
  ],
  updates: [
    {
      id: crypto.randomUUID(),
      text: "Created the PauleauZ luxury property landing page and committed changes.",
      at: new Date().toISOString()
    }
  ]
};

function load() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultData));
    return structuredClone(defaultData);
  }
  try {
    return JSON.parse(raw);
  } catch {
    return structuredClone(defaultData);
  }
}

function save(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

let data = load();

const statuses = ["todo", "doing", "done"];
const labels = { todo: "To Do", doing: "In Progress", done: "Done" };

function renderMetrics() {
  const total = data.tasks.length;
  const done = data.tasks.filter(t => t.status === "done").length;
  const doing = data.tasks.filter(t => t.status === "doing").length;
  const todo = data.tasks.filter(t => t.status === "todo").length;
  const rate = total ? Math.round((done / total) * 100) : 0;

  const cards = [
    ["Total Tasks", total],
    ["Completion Rate", `${rate}%`],
    ["In Progress", doing],
    ["Pending", todo]
  ];

  document.getElementById("metrics").innerHTML = cards
    .map(([name, value]) => `<article class="card"><h3>${name}</h3><strong>${value}</strong></article>`)
    .join("");
}

function nextStatus(status) {
  const idx = statuses.indexOf(status);
  return statuses[(idx + 1) % statuses.length];
}

function renderBoard() {
  const board = document.getElementById("board");
  board.innerHTML = "";

  statuses.forEach(status => {
    const col = document.createElement("div");
    col.className = "column";
    col.innerHTML = `<h3>${labels[status]}</h3>`;

    data.tasks
      .filter(task => task.status === status)
      .forEach(task => {
        const tpl = document.getElementById("taskTemplate");
        const node = tpl.content.firstElementChild.cloneNode(true);
        node.querySelector("h4").textContent = task.title;
        node.querySelector("p").textContent = task.details;
        node.querySelector(".meta").textContent = `Updated: ${new Date(task.updatedAt).toLocaleString()}`;

        node.querySelector(".move").addEventListener("click", () => {
          task.status = nextStatus(task.status);
          task.updatedAt = new Date().toISOString();
          save(data);
          render();
        });

        node.querySelector(".delete").addEventListener("click", () => {
          data.tasks = data.tasks.filter(t => t.id !== task.id);
          save(data);
          render();
        });

        col.appendChild(node);
      });

    board.appendChild(col);
  });
}

function renderUpdates() {
  const updates = [...data.updates].sort((a, b) => b.at.localeCompare(a.at));
  document.getElementById("updates").innerHTML = updates
    .map(
      u => `<li>${u.text}<time>${new Date(u.at).toLocaleString()}</time></li>`
    )
    .join("");
}

function bindActions() {
  document.getElementById("addTaskBtn").addEventListener("click", () => {
    const title = prompt("Task title:");
    if (!title) return;
    const details = prompt("Task details:", "") || "";
    data.tasks.push({
      id: crypto.randomUUID(),
      title,
      details,
      status: "todo",
      updatedAt: new Date().toISOString()
    });
    save(data);
    render();
  });

  document.getElementById("addUpdateBtn").addEventListener("click", () => {
    const text = prompt("Update note:");
    if (!text) return;
    data.updates.push({
      id: crypto.randomUUID(),
      text,
      at: new Date().toISOString()
    });
    save(data);
    render();
  });
}

function render() {
  renderMetrics();
  renderBoard();
  renderUpdates();
}

bindActions();
render();
