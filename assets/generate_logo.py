"""
Genera el logo de md2latex como PNG puro (sin dependencias externas).

Diseño: fondo oscuro (Catppuccin Mocha), "md2" en azul (escala 3×)
        y "LaTeX" en naranja (escala 2×), separados por una línea fina.
"""

import struct
import zlib
from pathlib import Path


# ── Paleta (Catppuccin Mocha) ────────────────────────────────────────────────
BG      = (30,  30,  46)   # #1e1e2e  fondo
BLUE    = (137, 180, 250)  # #89b4fa  "md2"
ORANGE  = (250, 179, 135)  # #fab387  "LaTeX"
DIVIDER = (108, 112, 134)  # #6c7086  línea divisoria

W, H = 128, 128


# ── Utilidades PNG ────────────────────────────────────────────────────────────

def _chunk(tag: bytes, data: bytes) -> bytes:
    c = tag + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)


def save_png(path: str, pixels: list):
    h = len(pixels)
    w = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b in row:
            raw += bytes([r, g, b])
    sig  = b'\x89PNG\r\n\x1a\n'
    ihdr = _chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    idat = _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    iend = _chunk(b'IEND', b'')
    Path(path).write_bytes(sig + ihdr + idat + iend)


# ── Canvas ────────────────────────────────────────────────────────────────────

def new_canvas(w, h, color=BG) -> list:
    return [[color] * w for _ in range(h)]


def fill_rect(px, x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            px[y][x] = color


def draw_line_h(px, x0, x1, y, thickness, color):
    fill_rect(px, x0, y - thickness // 2, x1, y + (thickness + 1) // 2, color)


def draw_rounded_rect(px, x0, y0, x1, y1, r, color):
    fill_rect(px, x0 + r, y0,     x1 - r, y1,     color)
    fill_rect(px, x0,     y0 + r, x1,     y1 - r, color)
    for dy in range(r + 1):
        for dx in range(r + 1):
            if dx * dx + dy * dy <= r * r:
                fill_rect(px, x0 + r - dx, y0 + r - dy, x0 + r - dx + 1, y0 + r - dy + 1, color)
                fill_rect(px, x1 - r + dx, y0 + r - dy, x1 - r + dx + 1, y0 + r - dy + 1, color)
                fill_rect(px, x0 + r - dx, y1 - r + dy, x0 + r - dx + 1, y1 - r + dy + 1, color)
                fill_rect(px, x1 - r + dx, y1 - r + dy, x1 - r + dx + 1, y1 - r + dy + 1, color)


# ── Fuente bitmap 5×7 ─────────────────────────────────────────────────────────
# Cada fila es un entero de 5 bits: el bit más significativo = píxel izquierdo.

FONT = {
    'm': [0b00000, 0b00000, 0b11011, 0b10101, 0b10101, 0b10101, 0b00000],
    'd': [0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b01111, 0b00000],
    '2': [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b11111, 0b00000],
    'L': [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111, 0b00000],
    'a': [0b00000, 0b00000, 0b01110, 0b10001, 0b01111, 0b10001, 0b01111],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000],
    'e': [0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01111],
    'X': [0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b00000, 0b00000],
}


def draw_char(px, ch: str, x: int, y: int, scale: int, color):
    for row_i, bits in enumerate(FONT.get(ch, [0] * 7)):
        for col_i in range(5):
            if bits & (1 << (4 - col_i)):
                px_x = x + col_i * scale
                px_y = y + row_i * scale
                fill_rect(px, px_x, px_y, px_x + scale, px_y + scale, color)


def draw_text(px, text: str, x: int, y: int, scale: int, color, gap: int = 1):
    """gap: espacio entre caracteres en unidades de fuente (se multiplica por scale)."""
    cx = x
    for ch in text:
        draw_char(px, ch, cx, y, scale, color)
        cx += (5 + gap) * scale


def text_width(text: str, scale: int, gap: int = 1) -> int:
    return len(text) * 5 * scale + (len(text) - 1) * gap * scale


# ── Diseño del logo ───────────────────────────────────────────────────────────

def draw_logo() -> list:
    px = new_canvas(W, H)

    # Fondo con esquinas redondeadas (ligeramente más claro que el canvas)
    PANEL = (40, 40, 59)  # #28283b – surface0 Catppuccin
    draw_rounded_rect(px, 6, 6, 121, 121, 16, PANEL)

    # ── "md"  escala 3×, en AZUL ──────────────────────────────────────────────
    s1, g1 = 3, 1
    w1 = text_width('md', s1, g1)
    x1 = (W - w1) // 2
    y1 = 38
    draw_text(px, 'md', x1, y1, s1, BLUE, g1)

    # ── Línea divisoria ───────────────────────────────────────────────────────
    sep_y = y1 + 7 * s1 + 5
    draw_line_h(px, 22, 105, sep_y, 1, DIVIDER)

    # ── "LaTeX"  escala 2×, en NARANJA ───────────────────────────────────────
    s2, g2 = 2, 1
    w2 = text_width('LaTeX', s2, g2)
    x2 = (W - w2) // 2
    y2 = sep_y + 6
    draw_text(px, 'LaTeX', x2, y2, s2, ORANGE, g2)

    return px


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    out = Path(__file__).parent / 'logo.png'
    pixels = draw_logo()
    save_png(str(out), pixels)
    print(f'Logo guardado en: {out}')
