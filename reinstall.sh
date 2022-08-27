#!/bin/sh

python -m build && pip install dist/SMake-0.0.1-py3-none-any.whl --force-reinstall
