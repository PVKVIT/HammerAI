# ⬡ HammerAI — CAD Assistant

> Generative CAD from natural language, powered by **Google Gemini** · **CadQuery** · **PyVista**

---

## Features

| Feature | Description |
|---|---|
| 🤖 AI-Driven CAD | Describe a part in plain English; Gemini generates valid CadQuery code |
| 🧊 3-D Viewport | Interactive PyVista viewport with orbit, pan, zoom |
| ⚡ Stress Simulation | Visual FEA-style stress heatmap with **node / face selection** for force application |
| 🏭 Manufacturing Estimator | Cost, time, and energy estimates for CNC / 3D Print / Injection Molding |
| 📦 Component Library | Pre-built Bolt, Nut, Screw, Washer, Coupling, Connector templates |
| 🕘 Workflow History | Full undo/redo tree; double-click any version to restore it |
| 🎨 Themes | Dark Hacker · Midnight Blue · Solarized Dark · Light |

---

## Project Structure

```
HammerAI/
│
├── Hammer.py                  ← Entry point  (run this)
│
├── config/
│   ├── constants.py           ← App-wide constants (paths, URLs, versions)
│   ├── themes.json            ← UI colour palettes (edit to add themes)
│   ├── components.json        ← Component library CadQuery snippets
│   ├── manufacturing.json     ← Materials & method cost/speed data
│   └── manufacturing.py      ← Loads manufacturing.json into Python dicts
│
├── core/
│   ├── gemini_client.py       ← Gemini REST API wrapper + APIWorker thread
│   ├── cad_manager.py         ← CADModelManager + SafetyExecutor
│   ├── workflow.py            ← Versioned undo/redo history manager
│   ├── manufacturing.py       ← ManufacturingEstimator (pure logic)
│   └── cad_utils.py           ← Feature-tree parser, CADQUERY_OPS list
│
├── ui/
│   ├── theme.py               ← Theme engine — loads themes.json, builds QSS
│   ├── splash.py              ← Animated startup splash screen
│   ├── main_window.py         ← MainWindow (top-level app shell)
│   ├── chat_panel.py          ← ChatBubble + ChatPanel
│   ├── workspace.py           ← WorkspaceViewer + OverlayFeatureTree
│   ├── toolbar_panel.py       ← Left sidebar (Library / Workflow / Tools)
│   ├── settings_dialog.py     ← Settings modal (API · Theme · Layout)
│   ├── simulation_window.py   ← Stress simulation + node-pick UI  ← UPDATED
│   └── manufacturing_window.py← Manufacturing analysis dialog
│
├── data/                      ← Auto-created at runtime
│   ├── cad_session.json       ← Autosave (latest session)
│   └── cad_settings.json      ← User settings persistence
│
└── requirements.txt
```

---

## Quick Start

```bash
# 1. Clone / download
git clone https://github.com/your-org/HammerAI.git
cd HammerAI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python Hammer.py
```

> **Tip:** On first launch, paste your **Google Gemini API key** (`AIza…`) into the navbar and click **Activate**.

---

## Simulation — Force Node Selection (New)

The Stress Simulation window now lets you choose *where* the force is applied:

1. **Named Region** — pick from the combo box:  
   `Top Face (+Z max)`, `Bottom Face (-Z min)`, `Front`, `Back`, `Right`, `Left`, or `Mesh Centre`.

2. **Interactive Node Pick** — click **"Enter Node-Pick Mode"**, then click any point on the 3-D mesh.  
   The picked coordinates are shown, and a red sphere marks the origin when you run the simulation.

3. **Clear** the pick with the **"✕ Clear Picked Node"** button to return to the named-region selection.

---

## Adding Themes

Edit `config/themes.json` and add a new entry following the existing pattern:

```json
"My Theme": {
  "bg":      "#111111",
  "panel":   "#222222",
  "border":  "#333333",
  "text":    "#eeeeee",
  "accent":  "#ff6600",
  "hover":   "#cc5500",
  "dim":     "#888888",
  "danger":  "#ff3333",
  "user_bg": "#2a1a0a",
  "user_bd": "#ff6600"
}
```

The theme will appear automatically in **Settings → Theme** at next launch.

---

## Adding Components

Edit `config/components.json` and add a new key/value pair:

```json
"My Part": "result = cq.Workplane('XY').box(30, 20, 10)"
```

The component will appear in the **Library** tab immediately.

---
