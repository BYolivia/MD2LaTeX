#!/bin/bash
# Instalador de md2latex
set -e

INSTALL_DIR="/opt/md2latex"
BIN_LINK="/usr/local/bin/md2latex"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Instalando md2latex en $INSTALL_DIR..."

sudo mkdir -p "$INSTALL_DIR"
sudo cp -r "$SCRIPT_DIR/md2latex/." "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/md2latex"
sudo ln -sf "$INSTALL_DIR/md2latex" "$BIN_LINK"

echo ""
echo "Instalación completada."
echo "Ejecuta 'md2latex' para iniciar la aplicación."
