# HammerAI — Architecture & Design Document

## Overview

HammerAI follows a **layered MVC-inspired architecture** split across three
top-level packages:

```
config/   – static data & constants (no imports from ui/ or core/)
core/     – pure business logic (no Qt imports)
ui/       – Qt widgets & windows (imports from core/ and config/)
```

`Hammer.py` is the sole entry point and only imports from `ui/` and `config/`.

---

## Dependency Graph

```
Hammer.py
  └── ui/main_window.py
        ├── ui/chat_panel.py
        ├── ui/workspace.py
        │     └── core/cad_utils.py
        ├── ui/toolbar_panel.py
        │     ├── config/components.json  (via json.load)
        │     └── core/workflow.py
        ├── ui/settings_dialog.py
        │     └── ui/theme.py  ←── config/themes.json
        ├── ui/simulation_window.py
        │     ├── core/cad_manager.py
        │     └── config/manufacturing.py
        ├── ui/manufacturing_window.py
        │     ├── core/manufacturing.py
        │     └── config/manufacturing.py
        ├── core/gemini_client.py
        ├── core/cad_manager.py
        │     └── core/cad_utils.py  (indirectly via workspace)
        └── core/workflow.py
```

---

## Module Responsibilities

### `config/`

| File | Purpose |
|---|---|
| `constants.py` | Single source of truth for APP_NAME, VERSION, file paths, API URLs |
| `themes.json` | All colour palettes — edit here to add/remove themes, no Python changes needed |
| `components.json` | CadQuery snippet library — add new parts without touching Python |
| `manufacturing.json` | Material costs, densities, method factors — fully data-driven |
| `manufacturing.py` | Thin loader that exposes MATERIALS_DB and METHOD_FACTORS dicts |

### `core/`

| File | Purpose |
|---|---|
| `gemini_client.py` | GeminiClient (sync REST call) + APIWorker (QThread wrapper) |
| `cad_manager.py` | CADModelManager (owns solid/mesh/code) + SafetyExecutor (sandboxed exec) |
| `workflow.py` | WorkflowManager (versioned list, pointer-based undo/redo, JSON serialisation) |
| `manufacturing.py` | ManufacturingEstimator.estimate() — pure function, zero side effects |
| `cad_utils.py` | parse_feature_tree() + CADQUERY_OPS constant list |

### `ui/`

| File | Purpose |
|---|---|
| `theme.py` | Loads themes.json, tracks active theme, generates QSS via build_stylesheet() |
| `splash.py` | SplashScreen widget with progress animation; emits `finished` signal |
| `main_window.py` | MainWindow — navbar, central layout, statusbar, signal wiring |
| `chat_panel.py` | ChatBubble (single message) + ChatPanel (scroll area + input) |
| `workspace.py` | WorkspaceViewer (PyVista QtInteractor) + OverlayFeatureTree |
| `toolbar_panel.py` | Left sidebar with Library / Workflow / Tools tabs |
| `settings_dialog.py` | SettingsDialog modal with API / Theme / Layout tabs |
| `simulation_window.py` | SimulationWindow — stress heatmap + **node/face force selection** |
| `manufacturing_window.py` | ManufacturingWindow — cost/time/energy estimation dialog |

---

## Data Flow — AI Generation

```
User types prompt
      │
      ▼
ChatPanel.message_submitted  →  MainWindow._on_chat_message()
                                       │
                                       ▼
                               APIWorker.run()  (QThread)
                                       │  calls
                                       ▼
                               GeminiClient.generate_cad_code()
                                       │  HTTP POST
                                       ▼
                               Gemini REST API
                                       │
                               response_ready signal
                                       ▼
                               MainWindow._on_api_response()
                                       │
                                       ▼
                               CADModelManager.load_code()
                                  SafetyExecutor.execute()
                                  CadQuery solid → STL → pv.PolyData
                                       │
                                       ▼
                               WorkspaceViewer.display_mesh()
                               WorkflowManager.add_version()
```

---

## Simulation — Node Selection Design

`SimulationWindow` supports two complementary force-origin strategies:

1. **Named region** (combo box) — maps to a `(x, y, z)` point derived from
   the mesh bounding box via `_region_origin()`.  
   Regions: Mesh Centre, Top/Bottom/Front/Back/Left/Right Face.

2. **Interactive point pick** — calls `plotter.enable_point_picking()` with
   `use_mesh=True`.  PyVista fires `_on_point_picked(point)` with the exact
   3-D coordinates of the clicked vertex.

The stress field is then computed as an exponential radial falloff from the
chosen origin point, providing an intuitive visual heatmap.

---

## Extending the Application

### Add a new theme
Edit `config/themes.json` — no Python changes required.

### Add a component template
Edit `config/components.json` — will appear in the Library tab automatically.

### Add a new manufacturing material
Edit `config/manufacturing.json` under `"materials"`.

### Add a new analysis window
1. Create `ui/my_analysis.py` extending `QDialog`.
2. Add a button to `ui/toolbar_panel.py` emitting a new signal.
3. Connect that signal in `ui/main_window.py`.

---

## Testing Strategy (Recommended)

| Layer | Tool | What to test |
|---|---|---|
| `core/` | `pytest` | SafetyExecutor, WorkflowManager undo/redo, ManufacturingEstimator maths |
| `core/gemini_client.py` | `pytest` + `responses` mock | API response parsing, error handling |
| `ui/` | `pytest-qt` | Widget creation, signal emission, settings round-trip |
