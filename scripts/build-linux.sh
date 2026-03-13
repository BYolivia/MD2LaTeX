#!/bin/bash
# Compila md2latex con PyInstaller dentro del contenedor Docker de cada distro.
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

echo "==> Compilando con PyInstaller..."
/opt/venv/bin/pyinstaller md2latex.spec

echo "==> Compilación completada."
