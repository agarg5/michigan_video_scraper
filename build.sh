#!/bin/bash
set -e

# Upgrade pip, setuptools, and wheel first
pip install --upgrade pip setuptools wheel

# Then install requirements
pip install -r requirements.txt

