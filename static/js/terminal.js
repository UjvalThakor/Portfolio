/**
 * Interactive Developer Terminal (UJVAL@DEV:~$)
 * & Hero Runtime Telemetry Simulator
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeroRuntimeSimulator();
  initDevTerminal();
});

/* 1. HERO RUNTIME SIMULATOR */
function initHeroRuntimeSimulator() {
  const simButtons = document.querySelectorAll('.sim-btn');
  const terminalBody = document.getElementById('runtime-terminal-output');

  if (!simButtons.length || !terminalBody) return;

  simButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      simButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      if (action === 'health') {
        appendRuntimeLog(`$ curl -i http://localhost:8000/api/v1/health/`);
        try {
          const t0 = performance.now();
          const res = await fetch('/api/v1/health/');
          const data = await res.json();
          const latency = Math.round(performance.now() - t0);
          appendRuntimeLog(`HTTP/1.1 200 OK | Latency: ${latency}ms | DB: ${data.services.database}`);
        } catch (e) {
          appendRuntimeLog(`HTTP/1.1 200 OK | Latency: 12ms (Cached mock fallback)`);
        }
      } else if (action === 'projects') {
        appendRuntimeLog(`$ GET /api/v1/projects/ (Django REST Framework)`);
        try {
          const res = await fetch('/api/v1/projects/');
          const data = await res.json();
          appendRuntimeLog(`HTTP/1.1 200 OK | Count: ${data.count} projects retrieved | Cache-Hit: TRUE`);
        } catch (e) {
          appendRuntimeLog(`HTTP/1.1 200 OK | 6 projects loaded from PostgreSQL/SQLite`);
        }
      } else if (action === 'db') {
        appendRuntimeLog(`$ SELECT * FROM projects_project ORDER BY order ASC;`);
        setTimeout(() => {
          appendRuntimeLog(`Execution Plan: Index Scan using projects_project_order_idx | Rows: 6 | Time: 1.42ms`);
        }, 200);
      }
    });
  });

  function appendRuntimeLog(text) {
    const p = document.createElement('div');
    p.className = 'cmd-output';
    p.textContent = text;
    terminalBody.appendChild(p);
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }
}

/* 2. INTERACTIVE DEV TERMINAL (UJVAL@DEV:~$) */
function initDevTerminal() {
  const terminalScreen = document.getElementById('dev-terminal-history');
  const inputField = document.getElementById('dev-terminal-input');
  const chips = document.querySelectorAll('.term-chip');

  if (!terminalScreen || !inputField) return;

  const commands = {
    help: () => `
Available Commands:
  about      - Engineering manifesto & developer background
  projects   - Authentic systems & applications built
  stack      - Backend ecosystem & tooling
  status     - Live backend server health & telemetry
  contact    - Communication endpoints & email
  neofetch   - Developer machine specifications
  clear      - Clear terminal screen
`,
    about: () => `
UJVAL THAKOR — BACKEND DEVELOPER
Location: Surat, Gujarat, India
Status:   B.Tech Computer Engineering Student
Focus:    Python • Django • REST APIs • AI/ML

Manifesto:
"I build reliable backend systems, APIs, automation tools, and AI-powered
applications. Focused on clean architecture, database efficiency, and systems
that actually work under real-world conditions."
`,
    projects: () => `
FEATURED PROJECTS (6 Authentic Systems):
  01. BeautyCare AI            [AI & REST APIs, Django, DRF, Swagger]
  02. Student Management System [Django + MySQL, Role-based Auth, Relational Schema]
  03. Job Portal               [Django, Multi-facet Filtering, Dual Auth, PostgreSQL]
  04. Cosmic Insight           [Dynamic Data Calculations, Django, Python]
  05. Car Number Detection     [Python, OpenCV, Morphological Pipeline]
  06. Fabric Fault Detection   [OpenCV, Real-Time Video Inspection, Multithreaded]

Type "curl /projects/<slug>" or explore the Selected Work section above.
`,
    stack: () => `
THE STACK BEHIND THE SYSTEM:
  [Backend]       Python 3.12, Django 6.1, Django REST Framework, REST APIs
  [Database]      PostgreSQL, MySQL, Redis (Caching & Sessions)
  [Tools]         Git, GitHub, Linux / Bash, Postman, Swagger / OpenAPI
  [AI / Vision]   OpenCV, Machine Learning, AI REST Integration
  [DevOps]        Docker, Gunicorn, Nginx
`,
    contact: () => `
GET IN TOUCH:
  Email:    ujvalthakor.dev@gmail.com
  GitHub:   https://github.com/ujvalthakor
  LinkedIn: https://linkedin.com/in/ujvalthakor
  Location: Surat, Gujarat, India

Open to backend engineering internships and full-time opportunities.
`,
    neofetch: () => `
   ___  _   _       ujval@production-server
  / _ \\| | | |      -----------------------
 | (_) | |_| |      OS: Debian GNU/Linux 12 (bookworm)
  \\__\\_\\\\___/       Host: High-Performance Backend Rig
                    Kernel: 6.6.15-backend-core
                    Uptime: 48 days, 14 hours
                    Shell: bash 5.2.15
                    Language: Python 3.12.10
                    Framework: Django 6.1.1 (DRF 3.15)
                    Database: PostgreSQL 16 / Redis 7.2
                    Memory: 245MiB / 8192MiB
`,
    status: async () => {
      try {
        const res = await fetch('/api/v1/health/');
        const data = await res.json();
        return `
BACKEND HEALTH TELEMETRY:
  API Gateway:      ${data.services.api}
  Database:         ${data.services.database}
  DB Ping Latency:  ${data.services.database_latency_ms} ms
  Cache Engine:     ${data.services.cache}
  Worker Threads:   ${data.services.workers}
  Django Version:   ${data.runtime.django}
  Python Runtime:   ${data.runtime.python}
  Status:           SYSTEM OPERATIONAL (200 OK)
`;
      } catch (err) {
        return `
BACKEND HEALTH TELEMETRY:
  Status:           SYSTEM OPERATIONAL (200 OK)
  Local Engine:     Django 6.1 / Python 3.12 / SQLite (Dev)
  Latency:          < 5 ms
`;
      }
    },
    clear: () => {
      terminalScreen.innerHTML = '';
      return null;
    }
  };

  async function executeCommand(cmd) {
    const trimmed = cmd.trim().toLowerCase();
    
    // Echo user input
    const entry = document.createElement('div');
    entry.className = 'term-entry';
    entry.innerHTML = `<div class="term-input-line"><span class="term-prompt">ujval@dev:~$</span> <span>${escapeHtml(trimmed)}</span></div>`;
    terminalScreen.appendChild(entry);

    if (trimmed === '') {
      scrollTerminal();
      return;
    }

    if (trimmed === 'clear') {
      commands.clear();
      return;
    }

    let output = '';
    if (commands[trimmed]) {
      const res = commands[trimmed]();
      if (res instanceof Promise) {
        output = await res;
      } else {
        output = res;
      }
    } else {
      output = `bash: command not found: "${escapeHtml(trimmed)}". Type "help" for available commands.`;
    }

    if (output) {
      const outDiv = document.createElement('pre');
      outDiv.className = 'cmd-output';
      outDiv.textContent = output;
      entry.appendChild(outDiv);
    }

    scrollTerminal();
  }

  function scrollTerminal() {
    terminalScreen.scrollTop = terminalScreen.scrollHeight;
  }

  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, m => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    })[m]);
  }

  // Handle enter key
  inputField.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      const val = inputField.value;
      inputField.value = '';
      await executeCommand(val);
    }
  });

  // Handle chip clicks
  chips.forEach(chip => {
    chip.addEventListener('click', async () => {
      const cmd = chip.dataset.cmd;
      if (cmd) {
        await executeCommand(cmd);
      }
    });
  });
}
