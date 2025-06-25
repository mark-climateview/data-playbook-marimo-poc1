#!/usr/bin/env python3
"""
Simplified script to inline util.py into Marimo notebooks before WASM export.
Replaces the 'import util' cell with the entire util.py content.
"""

import re
from pathlib import Path


def create_util_cell_content(util_file_path):
    """Read util.py and create a cell with all content indented by 4 spaces."""
    with open(util_file_path, 'r') as f:
        util_content = f.read()
    
    # Replace marimo-specific parts to work in inline context
    # Replace the try/except block for marimo import with just setting it to True
    util_content = util_content.replace(
        'try:\n    import marimo as mo\n    _MARIMO_AVAILABLE = True\nexcept ImportError:\n    _MARIMO_AVAILABLE = False',
        '# Marimo is available in the notebook context\n_MARIMO_AVAILABLE = True'
    )
    
    lines = util_content.split('\n')
    
    # Indent every non-empty line by 4 spaces
    indented_lines = []
    for line in lines:
        if line.strip() == '':  # Keep empty lines as-is
            indented_lines.append('')
        else:
            indented_lines.append('    ' + line)  # Indent by 4 spaces
    
    indented_util_content = '\n'.join(indented_lines)
    
    # Create the new cell content - using string concatenation to avoid f-string issues
    util_cell = '@app.cell\ndef __():\n    # Utility functions (inlined from util.py)\n' + indented_util_content + '\n    return translate, get_cbs_url, get_cbs_url_paginated, invalidate_cache, get_cache_stats, cleanup_fragmented_cache\n'
    
    return util_cell


def process_notebook(notebook_path, util_cell_content):
    """Replace the 'import util' cell with the util functions."""
    with open(notebook_path, 'r') as f:
        notebook_content = f.read()
    
    # Find and replace the cell that imports util
    target_text = '@app.cell\ndef _():\n    import util\n    return (util,)\n\n'
    replacement_text = util_cell_content + '\n\n'
    
    new_content = notebook_content.replace(target_text, replacement_text)
    
    # Replace all references to util.function_name with just function_name
    # since the functions are now available in the same scope
    new_content = re.sub(r'util\.', '', new_content)
    
    # Clean up function definitions that had util as a parameter
    # Handle cases like: def _(get_metadata, util):
    new_content = re.sub(r'def _\(([^)]*),\s*util\s*\):', r'def _(\1):', new_content)
    # Handle cases like: def _(util, get_metadata):
    new_content = re.sub(r'def _\(util,\s*([^)]*)\):', r'def _(\1):', new_content)
    # Handle cases like: def _(util):
    new_content = re.sub(r'def _\(util\):', 'def _():', new_content)
    
    # Clean up trailing commas in function definitions
    new_content = re.sub(r'def _\(([^)]*),\s*\):', r'def _(\1):', new_content)
    new_content = re.sub(r'def _\(\s*,\s*([^)]*)\):', r'def _(\1):', new_content)
    
    return new_content


def main():
    util_file = Path('util.py')
    if not util_file.exists():
        print("Error: util.py not found in current directory")
        return
    
    # Create the util cell content
    print("Reading util.py...")
    util_cell_content = create_util_cell_content(util_file)
    
    # Process all .py files that look like Marimo notebooks
    excluded_files = ["util.py", "exporter.py", "cache_manager.py"]
    notebook_files = []
    
    for f in Path('.').glob('*.py'):
        if f.name not in excluded_files:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    if 'marimo' in content and 'import util' in content:
                        notebook_files.append(f)
            except Exception:
                pass  # Skip files we can't read
    
    if not notebook_files:
        print("No Marimo notebook files found with 'import util'")
        return
    
    # Create export-ready versions
    export_dir = Path('export_ready')
    export_dir.mkdir(exist_ok=True)
    
    for notebook_file in notebook_files:
        print(f"Processing {notebook_file}...")
        
        try:
            new_content = process_notebook(notebook_file, util_cell_content)
            
            # Write the modified notebook
            export_file = export_dir / notebook_file.name
            with open(export_file, 'w') as f:
                f.write(new_content)
            
            print(f"Created export-ready version: {export_file}")
            
        except Exception as e:
            print(f"Error processing {notebook_file}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nExport-ready notebooks created in '{export_dir}' directory")
    print("You can now export these using:")
    for notebook_file in notebook_files:
        export_file = export_dir / notebook_file.name
        print(f"  marimo export html-wasm {export_file} -o {notebook_file.stem}_wasm")


if __name__ == "__main__":
    main()