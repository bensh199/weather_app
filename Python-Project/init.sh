#!/bin/bash

source .venv/bin/activate && gunicorn -w 3 -b 0.0.0.0:8000 main:app