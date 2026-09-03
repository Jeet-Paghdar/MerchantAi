#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- Installing Python Backend Dependencies ---"
pip install -r backend/requirements.txt

echo "--- Building React Frontend ---"
cd frontend
npm install
npm run build
cd ..

echo "--- Build Completed Successfully ---"

