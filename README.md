# PHREEQC Database Helper

## A Jupyter notebook and Python-based tool for exporting, searching, and editing PHREEQC databases

**PHREEQC Database Helper** is a small toolkit designed to support PHREEQC users who need to inspect and manage thermodynamic databases.  
This repository provides:

- a Jupyter notebook: `PHREEQCsearcher.ipynb`
- a Python GUI program: `PHREEQC_databasehelper.py`

Together, these tools allow you to:

- extract solution master species, solution species, and phase data from multiple PHREEQC database files,  
  merge them into a single table, and export the result to an Excel file
- search for selected species, reactions, or phases across different PHREEQC databases,  
  compare their definitions side-by-side, and export the results to Excel
- edit or add entries in an existing database file in order to update it or save it as a new database.

---

## How to use this project

### 1. Environment setup

This project uses [`uv`](https://docs.astral.sh/uv/) to manage its Python environment and dependencies, as defined in `pyproject.toml`.

#### How to install and activate the environment
1. Install `uv` if you don't already have it, following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/)
2. Download or clone this github repository
3. Open a terminal (e.g. the terminal in VS Code) and `cd` into the downloaded repository folder
4. Type in `dir` (Windows) or `ls` (macOS/Linux) and make sure you see `pyproject.toml` in the list of files that pops up; if not, your path is incorrect - redo step 3
5. Type in `uv sync` - this creates a local virtual environment (`.venv`) and installs all the required dependencies
6. To run any command inside this environment, prefix it with `uv run`, e.g. `uv run jupyter lab`
   - alternatively, activate the environment directly with `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows), after which you no longer need the `uv run` prefix

> **Note:** PHREEQC itself is **not** included in this repository.  
> You need to have PHREEQC installed separately if you plan to use the modified databases in your own simulations.

---

### 2. Jupyter notebook: `PHREEQCsearcher.ipynb`

1. Open the notebook, located at `docs/PHREEQCsearcher.ipynb`, in Jupyter (e.g. VS Code) using the installed environment.
   - if you are not opening it through an editor such as VS Code, run `uv run jupyter notebook docs/PHREEQCsearcher.ipynb`  
  (or `uv run jupyter lab docs/PHREEQCsearcher.ipynb` if you prefer JupyterLab)
2. Follow the instructions in each cell in order:
   - load one or more PHREEQC database files (`*.dat`),
   - select which species/phases to extract or search,
   - run the search and comparison routines.
3. The notebook will generate:
   - tables of solution master species, solution species, and phases
   - comparison tables across multiple databases
   - Excel files (`*.xlsx`) containing the extracted or compared data.

Each cell includes comments explaining what it does and which parameters you may want to change.

---

### 3. GUI program: `PHREEQC_databasehelper.py`

1. Place all PHREEQC database files you want to analyze (files ending in `.dat`) into the `src/pqcdbchk/build_database/databases` folder inside the project directory.
2. Run the script with `uv run python -m pqcdbchk.PHREEQC_databasehelper` from the project root (or, if you activated the environment directly, `python -m pqcdbchk.PHREEQC_databasehelper`).
3. A graphical user interface (GUI) window will appear. From this GUI, you can:
   - search for species, reactions, or phases by name or keyword, either by exact match or partial match
   - export the search results to an Excel file (You can specifically select the results you want to export. To select multiple rows, click Ctrl key       and click all the desired results. - if you don't, the program will ask you if you want to export all the data in the search result)
   - edit existing entries or add new entries and save the modified file
     either by overwriting the original database or by saving it under a new name.
     
> **Note:** When searching for chemical reactions, it is recommended to search using only the reactants, as the program is designed to internally normalize product names to enable comparison and matching across different databases.
> If you wish to search by the resulting species, you should add parentheses around the varying part of the chemical equation.
> _e.g., ZnCitrate- should be searched as Zn(Citrate)-_

The GUI is designed to guide you step-by-step through these operations using buttons and selection boxes,  
so that you can explore PHREEQC databases without manually editing text files.

---

## Output

Both the notebook and the GUI can export results to Excel files (`*.xlsx`).  
These files can be further processed, filtered, or plotted using your preferred tools (e.g. Excel, Python, R).

- Extracted database contents are exported as tables with one row per species or phase.
- Comparison results list the same species/phases across different databases side-by-side.
- Edited databases are saved in PHREEQC-compatible text format (`*.dat`).

---

### ⚠️ Current Limitations
* **Single Value Entry Only:** For now, the GUI is designed to add one value at a time. Multi-value or bulk additions are not yet supported and will be considered for future updates.

---
## Citation

If you use **PHREEQC Database Helper** in your work, please consider citing the corresponding JOSS paper (once published) as described here:

> *[Citation information will be added after acceptance by JOSS.]*

