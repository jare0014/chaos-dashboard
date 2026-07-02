---
status: ✅ Complete
type: AcademicProject
repo: Chaos Dashboard
---
[[Chaos Dashboard Case Study Note]]
# Chaos Dashboard
**Goal:** Build a Python simulation (Mandelbrot/Pendulum/3 body orbit) to practice NumPy/Matplotlib.
**Repo:** Cloud-hosted (Streamlit) — [Chaos Dashboard App](https://chaos-dashboard-khpbj6y6jeedqurug9j6m4.streamlit.app/)

## 📅 Milestones (The Sprints)

- [x] **Sprint 1: The Setup** (Jan 8 - Jan 15)
    - *Env config, Git init, "Hello World" scripts.*

- [x] **Sprint 2: The Logic** (Jan 16 - Jan 23)
    - *NumPy vectorization, Random Walks, basic Mandelbrot.*

- [x] **Sprint 3: The Visualization** (Jan 24 - Jan 31)
    - *Matplotlib static plots and saving imagery.*

- [x] **Sprint 4: The Interface (Current)** (Feb 1 - Feb 8)
    - *Completed Feb 8.*
    - **Deliverable A:** Streamlit Dashboard (Zoom/Pan).
    - **Deliverable B:** 3-Body Gravity (Intro to N-Body).
    - **Deliverable C: Polymer Simulator (Stochastic Physics).** - *Why:* The bridge between Random Walks and Structure.

- [x] **Sprint 5: The Dynamics** (Feb 9 - Feb 15)
    - *Goal: Double Pendulum Simulation.*
    - *Tech: The switch from Randomness (`numpy.random`) to Calculus (`scipy.integrate`).*

- [x] **Sprint 6: The Graph** (April 2026)
	- [x] Fix session state logic and v_mult
    - [x] Add technical papers and modular READMEs.*

## Dev Log History
```dataviewjs
const current = dv.current();
if (!current || !current.file) return;
const currentFileName = current.file.name;

// 1. Determine project keywords and git repository names to match
const cleanName = currentFileName
    .replace(/dev log/i, "")
    .replace(/project/i, "")
    .trim()
    .toLowerCase();

const slugName = cleanName.replace(/[^a-z0-9]+/g, "-");

// Collect repo candidates
let candidates = new Set([cleanName, slugName]);

// Support explicit repo names listed in the note's frontmatter
if (current.repo) {
    const repos = Array.isArray(current.repo) ? current.repo : [current.repo];
    for (const r of repos) {
        if (r) {
            candidates.add(r.trim().toLowerCase());
            candidates.add(r.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-"));
        }
    }
}

// Add known hardcoded fallbacks to maintain compatibility automatically
if (currentFileName.includes("Schedule Assistant")) {
    candidates.add("schedule-assistant-focus-timer");
    candidates.add("timeblocker and task timer");
}
if (currentFileName.includes("DRG")) {
    candidates.add("dynamical representation geometry");
}

const candidateList = Array.from(candidates);

// Filter out generic keywords for message-level matching
const genericNames = new Set(["untitled", "untitled.md", "dev log", "project", "log", "history", ""]);
const msgKeywords = candidateList.filter(c => c && !genericNames.has(c));

// 2. Fetch and process daily notes from "02_Journal/01_Daily"
const pages = dv.pages('"02_Journal/01_Daily"').sort(p => p.file.name, "desc");
const rows = [];

for (const p of pages) {
    const logs = [];
    
    // Check if this daily note explicitly links to this project page
    const projects = [].concat(p.Project || []);
    const isLinkedToThisProject = projects.some(proj => {
        if (proj && typeof proj === 'object' && proj.path) {
            return proj.path === current.file.path;
        }
        return String(proj).includes(currentFileName);
    });

    // A. Parse manual log entries (from Dev_Log or Log fields)
    const devLogs = [].concat(p.Dev_Log || []).concat(p.Log || []);
    for (const dl of devLogs) {
        if (!dl) continue;
        const dlStr = String(dl);
        const matchesManual = isLinkedToThisProject || 
                              dlStr.includes(currentFileName) || 
                              candidateList.some(cand => dlStr.toLowerCase().includes(cand));
        if (matchesManual && !logs.includes(dlStr)) {
            logs.push(dlStr);
        }
    }
    
    // B. Parse Antigravity Git Logs
    const content = await dv.io.load(p.file.path);
    if (content) {
        const gitLogRegex = /<!--\s*START(?:_|-)(?:antigravity|Antigravity)(?:_|-)(?:git|Git)(?:_|-)(?:log|Log)\s*-->([\s\S]*?)<!--\s*END(?:_|-)(?:antigravity|Antigravity)(?:_|-)(?:git|Git)(?:_|-)(?:log|Log)\s*-->/i;
        const match = content.match(gitLogRegex);
        if (match) {
            const gitBlock = match[1];
            const lines = gitBlock.split(/\r?\n/);
            let currentRepo = "";
            for (let line of lines) {
                line = line.trim();
                if (line.startsWith("**") && line.endsWith("**")) {
                    currentRepo = line.replace(/\*\*/g, '').trim().toLowerCase();
                } else if (line.startsWith("- ") && currentRepo) {
                    const commitLower = line.toLowerCase();
                    const repoMatches = candidateList.some(cand => 
                        currentRepo === cand || 
                        currentRepo.includes(cand) || 
                        cand.includes(currentRepo)
                    );
                    const messageMatches = msgKeywords.some(kw => commitLower.includes(kw));
                    
                    if (repoMatches || messageMatches) {
                        const logLine = "🐙 **Git Log**: " + line.substring(2);
                        if (!logs.includes(logLine)) {
                            logs.push(logLine);
                        }
                    }
                }
            }
        }
    }
    
    // C. Add to table if logs were found for this day
    if (logs.length > 0) {
        rows.push([p.file.link, logs.join("<br>")]);
    }
}

dv.table(["Date", "Notes"], rows);
```
