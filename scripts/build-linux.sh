#!/bin/bash
# Compila md2latex como bundle (onedir + tar.gz + install.sh).
# Detecta el gestor de paquetes automáticamente.
set -e

echo "==> Instalando dependencias del sistema..."
if command -v pacman &>/dev/null; then
    pacman -Syu --noconfirm python python-pip tk

elif command -v apt-get &>/dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
        python3 python3-pip python3-venv python3-tk tk-dev tcl-dev

elif command -v dnf &>/dev/null; then
    dnf install -y python3 python3-pip python3-tkinter tcl tk binutils

else
    echo "ERROR: gestor de paquetes no reconocido" >&2
    exit 1
fi

echo "==> Creando entorno virtual..."
python3 -m venv /opt/venv

echo "==> Instalando dependencias Python..."
/opt/venv/bin/pip install --quiet pyinstaller markdown tkinterweb

echo "==> Compilando con PyInstaller (onedir)..."
/opt/venv/bin/pyinstaller \
    --onedir \
    --name md2latex \
    --windowed \
    --add-data "assets:assets" \
    --add-data "language_colors:language_colors" \
    --add-data "editor_colors:editor_colors" \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.font \
    --hidden-import tkinterweb \
    --hidden-import markdown \
    --hidden-import "markdown.extensions" \
    --hidden-import "markdown.extensions.tables" \
    --hidden-import "markdown.extensions.fenced_code" \
    main.py

echo "==> Empaquetando bundle..."
cp scripts/install.sh dist/install.sh
chmod +x dist/install.sh
tar -czf dist/md2latex-linux.tar.gz -C dist md2latex install.sh

echo "==> Bundle creado: dist/md2latex-linux.tar.gz"
