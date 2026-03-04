#!/bin/bash

# set -e

echo "[BUILD] Nettoyage du dossier dist..."

echo "[BUILD] Création du paquet..."
python -m build --verbose

echo
echo "[UPLOAD] Authentification avec token PyPI (sera masqué)"
read -s -p "Token PyPI: " token
echo

python -m twine upload --username __token__ --password "$token" dist/*
