#!/bin/bash
# Compila md2latex y genera un .bundle autoextraíble.
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

echo "==> Empaquetando payload..."
tar -czf /tmp/payload.tar.gz -C dist md2latex

echo "==> Generando md2latex.bundle..."
cat > dist/md2latex.bundle << 'HEADER'
#!/bin/bash
# md2latex — instalador autoextraíble
set -e

INSTALL_DIR="/opt/md2latex"
BIN_LINK="/usr/local/bin/md2latex"

echo "md2LaTeX — instalador"
echo "====================="

# Extraer payload embebido al final de este script
TMPDIR=$(mktemp -d)
SKIP=$(awk '/^__PAYLOAD__$/{print NR+1; exit}' "$0")
tail -n +"$SKIP" "$0" | tar -xz -C "$TMPDIR"

echo "Instalando en $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r "$TMPDIR/md2latex/." "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/md2latex"
sudo ln -sf "$INSTALL_DIR/md2latex" "$BIN_LINK"

rm -rf "$TMPDIR"

echo ""
echo "Instalación completada."
echo "Ejecuta 'md2latex' para iniciar la aplicación."
exit 0

__PAYLOAD__
HEADER

# Adjuntar el payload binario al final del script
cat /tmp/payload.tar.gz >> dist/md2latex.bundle
chmod +x dist/md2latex.bundle

echo "==> Bundle creado: dist/md2latex.bundle"
