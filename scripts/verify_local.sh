#!/usr/bin/env bash
set -euo pipefail
python -m pytest -q
python -m compileall -q src
python -m imandrax_dgm.cli inventory