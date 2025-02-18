#!/bin/bash
source venv/bin/activate 2>/dev/null || true
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/test_pipeline.py -v --log-cli-level=INFO
