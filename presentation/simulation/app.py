#!/usr/bin/env python3
"""
Simple Flask UI to view and trigger generation of the dynamic bus GIF.

Usage:
  # In workspace terminal:
  pip install flask
  export FLASK_APP=presentation/simulation/app.py
  flask run --host=0.0.0.0 --port=8787

Open http://localhost:8787 in your browser. Click "Generate GIF" to run the generator script.
"""
import os
import subprocess
from flask import Flask, render_template_string, redirect, url_for

APP_ROOT = os.path.dirname(__file__)
GIF_PATH = os.path.join(APP_ROOT, 'dynamic_buses.gif')
SCRIPT_PATH = os.path.join(APP_ROOT, 'generate_dynamic_viz.py')

app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<title>Bus Dynamic Visualization</title>
<h1>Bus Dynamic Visualization</h1>
<form action="/generate" method="post">
  <button type="submit">Generate GIF</button>
</form>
{% if gif_exists %}
  <h2>Current GIF</h2>
  <img src="/static/dynamic_buses.gif" style="max-width:800px;">
{% else %}
  <p>No GIF found yet. Click Generate to create one.</p>
{% endif %}
'''

@app.route('/')
def index():
    gif_exists = os.path.exists(GIF_PATH)
    return render_template_string(TEMPLATE, gif_exists=gif_exists)

@app.route('/generate', methods=['POST'])
def generate():
    # Run generator script (blocking) - ensure we call python from system
    try:
        cmd = ['python3', SCRIPT_PATH]
        proc = subprocess.run(cmd, cwd=APP_ROOT, capture_output=True, text=True, timeout=300)
        print('Generate output:', proc.stdout)
        if proc.returncode != 0:
            print('Error:', proc.stderr)
    except Exception as e:
        print('Failed to run generator:', e)
    # copy gif to static folder if exists
    static_dir = os.path.join(APP_ROOT, 'static')
    os.makedirs(static_dir, exist_ok=True)
    if os.path.exists(GIF_PATH):
        try:
            import shutil
            shutil.copy(GIF_PATH, os.path.join(static_dir, 'dynamic_buses.gif'))
        except Exception as e:
            print('Failed to copy gif to static:', e)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # helper run
    app.run(host='0.0.0.0', port=8787)
