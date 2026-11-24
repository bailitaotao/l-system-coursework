#!/bin/sh
cd "$(dirname "$0")" || exit 1
# Try common macOS installations with Tk before the system Python.
for python_cmd in /usr/local/bin/python3 /opt/homebrew/bin/python3 python3; do
    if "$python_cmd" -c 'import tkinter,sys; sys.exit(sys.version_info < (3,8))' >/dev/null 2>&1; then
        exec "$python_cmd" app.py
    fi
done
echo "Install Python 3 with Tk, or open app.py in the same IDLE used for the starter."
read -r unused
