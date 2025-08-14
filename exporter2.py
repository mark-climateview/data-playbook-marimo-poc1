#!/usr/bin/env python3
"""
Simplified utility inliner for Marimo notebooks.
Replaces 'from util import ...' cells with inlined util.py content.
"""

import re
import subprocess
import shutil
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
    
    # Create the replacement cell with local data functions only
    cell_content = '@app.cell\ndef _(mo):\n    # Utility functions (inlined from util.py)\n'
    cell_content += ''.join(indented_lines)
    cell_content += '\n    return translate, get_local_data, get_data_file_path, list_available_data, check_data_availability, is_wasm, get_execution_environment, get_environment_info\n'
    
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


def clean_output_directory():
    """Remove existing HTML files from output directory."""
    output_dir = Path('output')
    if output_dir.exists():
        # Remove all HTML files except index.html (we'll recreate it)
        for html_file in output_dir.glob('*.html'):
            if html_file.name != 'index.html':
                print(f"Removing existing {html_file}")
                html_file.unlink()
        
        # Remove index.html if it exists (we'll create a new simple one)
        index_file = output_dir / 'index.html'
        if index_file.exists():
            print(f"Removing existing {index_file}")
            index_file.unlink()


def export_notebooks_to_html(notebooks):
    """Export notebooks to HTML using marimo export command."""
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    exported_files = []
    
    for notebook in notebooks:
        export_ready_file = Path('export_ready') / notebook.name
        output_file = output_dir / f"{notebook.stem}.html"
        
        print(f"Exporting {export_ready_file} to {output_file}...")
        
        try:
            # Run marimo export command
            cmd = [
                'uv', 'run', 'marimo', 'export', 'html-wasm',
                str(export_ready_file), '-o', str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Successfully exported {output_file}")
            exported_files.append(output_file)
            
        except subprocess.CalledProcessError as e:
            print(f"Error exporting {notebook}: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error exporting {notebook}: {e}")
    
    return exported_files


def copy_data_folder(destination_dir):
    """Copy the data/ folder to the destination directory."""
    source_data = Path('data')
    if not source_data.exists():
        print("Warning: data/ folder not found - notebooks may not work without data")
        return False
    
    dest_data = destination_dir / 'data'
    
    if dest_data.exists():
        print(f"Removing existing data folder at {dest_data}")
        shutil.rmtree(dest_data)
    
    print(f"Copying data/ folder to {dest_data}")
    shutil.copytree(source_data, dest_data)
    
    # Count files and calculate size
    data_files = list(dest_data.glob('*.parquet'))
    total_size = sum(f.stat().st_size for f in data_files) / (1024 * 1024)
    print(f"Copied {len(data_files)} data files ({total_size:.2f} MB)")
    
    return True


def generate_index_html(exported_files):
    """Generate a simple index.html file with links to exported notebooks."""
    output_dir = Path('output')
    index_file = output_dir / 'index.html'
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Playbooks - Climate Data Netherlands</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5rem;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 1rem 0;
            padding: 1rem;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
        a {
            text-decoration: none;
            color: #2c3e50;
            display: block;
            font-weight: 500;
        }
        a:hover {
            color: #3498db;
        }
        .description {
            font-size: 0.9rem;
            color: #7f8c8d;
            margin-top: 0.5rem;
        }
    </style>
</head>
<body>
    <h1>AI Data Playbooks - Climate Data Netherlands</h1>
    <p>Interactive data notebooks for climate data analysis and emission inventory modeling using the Transition Element Framework.</p>
    
    <ul>
"""
    
    for html_file in sorted(exported_files):
        # Extract a readable name from the filename
        filename = html_file.name
        display_name = filename.replace('.html', '').replace('_', ' ').title()
        if 'Data Table' in display_name:
            # Make CBS data table names more readable
            display_name = display_name.replace('Data Table', 'CBS Data Table')
        
        html_content += f"""        <li>
            <a href="{filename}">{display_name}</a>
            <div class="description">Interactive notebook - Click to explore the data</div>
        </li>
"""
    
    html_content += """    </ul>
</body>
</html>"""
    
    with open(index_file, 'w') as f:
        f.write(html_content)
    
    print(f"Generated {index_file}")


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
            if 'marimo' in content:
                notebooks.append(py_file)
        except:
            continue
    
    if not notebooks:
        print("No notebooks found with 'from util import'")
        return
    
    # Create export directory
    export_dir = Path('export_ready')
    export_dir.mkdir(exist_ok=True)
    
    # Copy data folder to export_ready directory
    print("Copying data/ folder to export_ready/...")
    copy_data_folder(export_dir)
    
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
    
    # Clean output directory and export to HTML
    print("\nCleaning output directory...")
    clean_output_directory()
    
    # Copy data folder to output directory for HTML exports
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    print("Copying data/ folder to output/...")
    copy_data_folder(output_dir)
    
    print("\nExporting notebooks to HTML...")
    exported_files = export_notebooks_to_html(notebooks)
    
    if exported_files:
        print("\nGenerating index.html...")
        generate_index_html(exported_files)
        print(f"\nPublished {len(exported_files)} notebooks to 'output/' directory")
        print("Open output/index.html in your browser to view all notebooks")
    else:
        print("\nNo notebooks were successfully exported")


if __name__ == "__main__":
    main()
