# Prototype Data Playbook for Climate Data in the Netherlands

This project uses Marimo to fetch data from various open data repositories and calculate certain parameters 
for modelling emission inventories and climate mitigation using the Transition Element Framework. 

Important notes and caveats:

- Never do anything in Git without asking me first
- Always use "uv" for all Python package related commands
  - E.g. "uv pip install <package>", or "uv run <program>"
- Maintain this file (@CLAUDE.md) but keep it very short and slim
- You can always run Marimo files directly, e.g. with "uv run data_table_85237NED.py", 
- After changing a Marimo file, run it in order to test if it works or if it generate errors;
  - A working file will generate no output, a broken file will give an Exception stack trace.

## Data Management (Local Data Approach)

- The project now uses a local data/ folder approach for better Marimo Community Cloud compatibility
- CBS data is stored locally in data/ folder as .parquet files (faster, more reliable)
- Use data_fetcher.py to fetch/refresh data from CBS APIs:
  - Run: "uv run data_fetcher.py" (fetch all datasets)
  - Run: "uv run data_fetcher.py --dataset 85236NED" (fetch specific dataset)
  - Run: "uv run data_fetcher.py --refresh" (force refresh all data)
- Notebooks use util.get_local_data() instead of live API calls
- Data files work both locally and on Marimo Community Cloud using mo.notebook_dir()

## Publishing Workflow

- Use exporter2.py to create and publish WASM-export-ready notebooks with inlined utilities
  - Creates export-ready/ directory with self-contained notebooks and data/ folder
  - Automatically exports all notebooks to HTML-WASM format in output/ directory  
  - Copies data/ folder to both export-ready/ and output/ directories
  - Generates index.html with navigation links to all published notebooks
  - Run: "uv run exporter2.py" (complete publishing workflow)

## Architecture

- Simple, clean architecture with local data files and translation utilities
- No complex caching or API management - just reliable local data access
- Optimized for both local development and Marimo Community Cloud deployment



