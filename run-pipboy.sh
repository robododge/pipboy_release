#!/bin/bash
# Launch the Pip-Boy UI fullscreen; refresh the INV (system info) screen first.
cd "$(dirname "$0")"
./getInfo > UIScreens/INV.txt 2>/dev/null
exec .venv/bin/python pipboyUI.py
