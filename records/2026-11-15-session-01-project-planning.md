# Session 01 — Project Planning (2026-11-14/15)

Planning session for a customized flight simulator built on **FlightGear**.
End goal: realistic physical peripherals. Current stage: no peripherals, control by mouse + keyboard.

---

## 1. Why FlightGear

- Not the most realistic simulator, but the most open: controls, scenery generation and aerodynamics can all be customized.
- A good way to learn every layer of the stack before adding hardware.

## 2. Licensing

- FlightGear is licensed under **GNU GPL v2**. Using, studying and modifying it is free, even commercially.
- GPL obligations apply only when **distributing** modified FlightGear: the source must then be shared under the same license.
- Each aircraft and scenery package has its own license (mostly GPL). Check before redistributing.
- Decision for this repo: release it under **GPL-2.0-or-later** for simplicity.

## 3. Languages: where each one is used

| Layer | Language | Purpose |
|---|---|---|
| Config / bindings | XML (FG PropertyList) | Aircraft definitions, keyboard/joystick mapping, autopilot, instruments, I/O protocols |
| In-sim logic | Nasal (FG's built-in scripting language) | Aircraft systems, custom behavior, dialogs |
| Aerodynamics | JSBSim XML (or YASim) | Flight dynamics, engines, mass and balance |
| External tools / peripherals | **Python** (main language) | Read/write sim state, logging, dashboards, hardware bridges |
| Peripheral firmware (later) | C++ (Arduino) | Panel and switch boards |
| FG core | C++ | Only when changing the engine itself |

All sim state lives in the **property tree** (e.g. `/controls/flight/aileron`).
Python accesses it from outside FG through:
- `--telnet=5401`: simple text commands; the easiest place to start
- `--httpd=8080`: browser property viewer plus JSON/WebSocket
- `--generic=socket,...,udp,<protocol>`: fast UDP streaming in a format defined by an XML file. This is the standard route for peripherals.

Future peripheral data flow: `hardware → Python/Arduino → UDP (generic protocol) → property tree`.

## 4. Source vs. installer

- Official source lives on **GitLab** (`gitlab.com/flightgear`: `flightgear`, `simgear`, `fgdata`). GitHub copies are mirrors.
- Building from source (C++, CMake, Qt, OpenSceneGraph, VS2022) is needed only to change the core engine.
- About 95% of customization is data (XML, Nasal, JSBSim) plus external programs, so it works with the official binary.

### Levels of "fully customizable"

| Level | Scope | Needs |
|---|---|---|
| 1. Data | Aircraft, aero, Nasal, GUI, shaders, protocols, bindings | Official binary + `fgdata` of the same version |
| 2. Read core | Read and search all C++ | Source submodules (no build) |
| 3. Modify core | Change the engine | Full Windows build toolchain |

**Decision:** start at levels 1 and 2. Move to level 3 only if data-level customization isn't enough.

## 5. Self-contained, reproducible repo

Goal: everything that matters lives in this workspace, so others can clone and run it on their own machines.

- **Don't commit** FlightGear itself. `fgdata` is several GB, scenery is tens of GB, and GitHub rejects files over 100 MB.
- **Reference** FG as **git submodules pinned to one release** (e.g. 2024.1): readable and editable locally, and identical for everyone.
- Launch FG with paths pointing into the repo, so everything FG loads comes from the workspace:
  `--fg-root=external/fgdata --fg-aircraft=aircraft --addon=addons/... --terrasync-dir=<gitignored cache>`
- Changes to upstream files (`fgdata`/core) go into **your own fork**, with the submodule pointed at that fork.

### Proposed layout

```
2611-flight-sim/
├─ external/        # submodules: fgdata, flightgear, simgear (pinned, shallow)
├─ addons/          # in-sim customizations (Nasal + XML), loaded via --addon
├─ aircraft/        # aircraft forks (aero/JSBSim edits)
├─ protocols/       # generic-protocol XML (installed into FG's Protocol dir)
├─ input/           # keyboard/joystick bindings
├─ python/          # external tools + requirements.txt (own venv)
├─ scripts/
│  ├─ setup.ps1     # one-shot: submodules, venv, protocol install, checks
│  └─ fly.ps1       # launch FG with everything pointing into the repo
├─ versions.json    # pinned FG version + checksums
├─ records/         # session notes (this file)
└─ README.md        # requirements, hardware, setup steps
```

Why the folders are separate: each kind of file runs somewhere different.
- `python/` runs **outside** FG and has its own venv.
- `nasal/` and `addons/` run **inside** FG, which must be told where to find them.
- `protocols/` are message-format definitions that **both** FG and Python must agree on.

Create the folders gradually, when each stage needs them.

## 6. OneDrive: move the repo out

The repo currently sits in `OneDrive\02-Lives\projects\`. Problems even when working on a single device:

- **File locking** during upload → git / pip / build errors (`index.lock`, `Permission denied`)
- **Conflict copies** (`*-DESKTOP-*`). These have already appeared; see `.gitignore`.
- **Files On-Demand / Storage Sense** turning files into cloud-only placeholders → stalls and failures
- **Sync volume**: GBs of small files, background CPU/disk/network use, cloud storage quota
- **`.git` corruption** risk: OneDrive syncs a consistent database as unrelated individual files
- **Long paths**: the OneDrive prefix uses about 55 of Windows' 260 characters
- **Symlinks/junctions** handled badly
- Adds nothing once GitHub is the backup

**Decision (pending):** move the repo to `C:\dev\2611-flight-sim` and use GitHub as the backup.
Fallback: keep the repo in OneDrive but put heavy folders (submodules, venv, cache, build) outside it.

## 7. What to install (Windows 11)

| Tool | Purpose |
|---|---|
| FlightGear 2024.1 installer (flightgear.org) | Official binary (update the GPU driver first) |
| Git | Version control + submodules |
| Python 3.12+ (`winget install Python.Python.3.12`) | External tooling |
| Python packages: `flightgear-python`, `requests`, `websocket-client`, `jsbsim` (later `pyserial`) | Talk to FG; run JSBSim on its own |
| VS Code + Python extension (+ a Nasal syntax extension) | Editing |
| Later: Blender, Arduino IDE / PlatformIO | Models, peripheral firmware |

FG paths on Windows: FG_ROOT is `C:\Program Files\FlightGear 2024.1\data` (to be replaced by `external/fgdata`). FG_HOME is `%APPDATA%\flightgear.org`.

## 8. Roadmap

| Stage | Goal | Done when |
|---|---|---|
| **0 — Fly it** *(current)* | Install, scaffold the repo, fly with mouse + keyboard | Full circuit flown; Python prints live altitude/airspeed |
| 1 — Understand it | Property tree, launch options, logs | Can find any instrument's property |
| 2 — Python control | Telnet/HTTP read and write | Script logs flight data to CSV and moves a control |
| 3 — UDP streaming | Generic protocol + Python UDP | 30 Hz telemetry in, controls out |
| 4 — In-sim customization | Custom bindings + a Nasal add-on | Your own key or feature works |
| 5 — Aerodynamics | Fork the aircraft, edit JSBSim, compare with standalone `jsbsim` | Change in behavior is measurable |
| 6 — Peripherals | Arduino/HID → Python → FG | A physical control drives the sim |

## 9. Stage 0 checklist (next steps)

- [ ] Move the repo out of OneDrive to `C:\dev\2611-flight-sim`
- [ ] Install Git, Python 3.12, FlightGear 2024.1
- [ ] Scaffold: folders, `.gitignore`, `LICENSE` (GPL-2.0-or-later), `versions.json`, `requirements.txt`
- [ ] Add `external/` submodules (shallow, pinned to 2024.1)
- [ ] Write `scripts/setup.ps1` and `scripts/fly.ps1`
- [ ] First flight: C172P at KSFO, using the repo's own `fgdata`
- [ ] Learn the controls: right-click cycles the mouse mode (pointer → **yoke** → view); arrows/numpad = flight controls; `PgUp/PgDn` throttle; `b` parking brake; `,` `.` brakes; `[` `]` flaps; `v` view; `p` pause; `?` key list. Use Help → Tutorials (C172P).
- [ ] Explore Debug → Browse Internal Properties
- [ ] Python reads `/position/altitude-ft` and airspeed live (`--telnet=5401 --httpd=8080`)
- [ ] Push to GitHub; test a fresh clone + `setup.ps1`
- [ ] Record graphics settings, FPS, issues and launch options in `records/`
