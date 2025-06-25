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
- The project uses intelligent caching for CBS data APIs (cache/ directory)
  - Use util.get_cbs_url_paginated() for large TypedDataSet endpoints
  - See CACHE_README.md for details
- Use exporter2.py to create WASM-export-ready notebooks with inlined utilities
  - Creates export-ready/ directory with self-contained notebooks
  - Run: "uv run exporter2.py" then "marimo export html-wasm export_ready/<file> -o <output>"



