#!/usr/bin/env python3
"""
Simplified utility inliner for Marimo notebooks.
Replaces 'from util import ...' cells with inlined util.py content.
"""

import re
from pathlib import Path


def create_inlined_util_cell():
    """Read util.py, strip basic imports, and create indented cell content."""
    with open('util.py', 'r') as f:
        lines = f.readlines()
    
    # Skip only the imports that are already in the notebook
    # Keep typing imports and other necessary imports for util.py
    skip_patterns = [
        'import requests',
        'import json', 
        'import pandas as pd'
    ]
    
    # Also need to handle the marimo import differently since mo is passed as parameter
    marimo_block_start = -1
    marimo_block_end = -1
    
    util_lines = []
    skip_marimo_block = False
    
    for i, line in enumerate(lines):
        # Skip basic imports but keep typing and other necessary imports
        if any(pattern in line.strip() for pattern in skip_patterns):
            continue
            
        # Handle marimo import block specially
        if 'try:' in line and i+1 < len(lines) and 'import marimo as mo' in lines[i+1]:
            skip_marimo_block = True
            util_lines.append('# marimo available as parameter\n')
            util_lines.append('_MARIMO_AVAILABLE = True\n')
            continue
        elif skip_marimo_block and 'except ImportError:' in line:
            continue
        elif skip_marimo_block and '_MARIMO_AVAILABLE = False' in line:
            skip_marimo_block = False
            continue
        elif skip_marimo_block:
            continue
            
        util_lines.append(line)
    
    # Remove any remaining empty lines at the start
    while util_lines and util_lines[0].strip() == '':
        util_lines.pop(0)
    
    # Indent all lines by 4 spaces
    indented_lines = []
    for line in util_lines:
        if line.strip() == '':
            indented_lines.append('\n')  # Keep empty lines
        else:
            indented_lines.append('    ' + line)  # Indent by 4 spaces
    
    # Create the replacement cell
    cell_content = '@app.cell\ndef _(mo):\n    # Utility functions (inlined from util.py)\n'
    cell_content += ''.join(indented_lines)
    cell_content += '\n    return translate, get_cbs_url, get_cbs_url_paginated, invalidate_cache, get_cache_stats, cleanup_fragmented_cache\n'
    
    return cell_content


def process_notebook(notebook_path):
    """Replace the util import cell with inlined util functions."""
    with open(notebook_path, 'r') as f:
        content = f.read()
    
    # Find the util import cell using string operations instead of regex
    lines = content.split('\n')
    in_import_cell = False
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip() == '@app.cell' and i+1 < len(lines) and 'def _():' in lines[i+1]:
            if i+2 < len(lines) and 'from util import' in lines[i+2]:
                start_idx = i
                in_import_cell = True
        elif in_import_cell and line.strip().startswith('return'):
            end_idx = i
            break
    
    if start_idx == -1 or end_idx == -1:
        print(f"Warning: Could not find util import cell in {notebook_path}")
        return content
    
    # Replace the cell
    replacement = create_inlined_util_cell()
    new_lines = lines[:start_idx] + replacement.split('\n') + lines[end_idx+2:]
    
    return '\n'.join(new_lines)


def main():
    """Process all Marimo notebooks and create export-ready versions."""
    util_file = Path('util.py')
    if not util_file.exists():
        print("Error: util.py not found")
        return
    
    # Find notebooks with util imports
    notebooks = []
    for py_file in Path('.').glob('*.py'):
        if py_file.name in ['util.py', 'exporter.py', 'exporter2.py', 'cache_manager.py']:
            continue
        
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            if 'from util import' in content and 'marimo' in content:
                notebooks.append(py_file)
        except:
            continue
    
    if not notebooks:
        print("No notebooks found with 'from util import'")
        return
    
    # Create export directory
    export_dir = Path('export_ready')
    export_dir.mkdir(exist_ok=True)
    
    # Process each notebook
    for notebook in notebooks:
        print(f"Processing {notebook}...")
        try:
            new_content = process_notebook(notebook)
            export_file = export_dir / notebook.name
            
            with open(export_file, 'w') as f:
                f.write(new_content)
            
            print(f"Created: {export_file}")
        except Exception as e:
            print(f"Error processing {notebook}: {e}")
    
    print(f"\nExport-ready files in '{export_dir}/'")
    print("Export with: marimo export html-wasm <file> -o <output>")


if __name__ == "__main__":
    main()