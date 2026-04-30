#!/bin/bash

# set -e

echo "[BUILD] Nettoyage des caches Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "[BUILD] Nettoyage du dossier dist..."
if [ -d "dist" ]; then
    rm -rf dist
fi

echo "[BUILD] Création du paquet..."
python -m build --verbose

echo
echo "[UPLOAD] Authentification avec token PyPI (sera masqué)"
read -s -p "Token PyPI: " token
echo

python -m twine upload --username __token__ --password "$token" dist/*
