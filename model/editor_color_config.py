"""Configuración de colores del resaltado de sintaxis en los paneles de edición."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

EDITOR_COLORS_FOLDER = Path(__file__).parent.parent / "editor_colors"


# ---------------------------------------------------------------------------
# Helpers de persistencia
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Colores del editor Markdown
# ---------------------------------------------------------------------------

@dataclass
class MdEditorColors:
    """Colores para el resaltado de sintaxis Markdown."""
    heading: str          = "#89b4fa"
    heading_bold: bool    = True
    bold_text: str        = "#f5c2e7"
    italic_text: str      = "#f9e2af"
    inline_code: str      = "#a6e3a1"
    inline_code_bg: str   = "#11111b"
    code_block: str       = "#a6e3a1"
    code_block_bg: str    = "#11111b"
    link: str             = "#89dceb"
    quote: str            = "#a6adc8"
    quote_italic: bool    = True
    hr_color: str         = "#45475a"
    list_marker: str      = "#fab387"
    strikethrough: str    = "#6c7086"

    _FILE = EDITOR_COLORS_FOLDER / "md_editor.json"

    def save(self):
        _save_json(self._FILE, asdict(self))

    @classmethod
    def load(cls) -> MdEditorColors:
        if not cls._FILE.exists():
            obj = cls()
            obj.save()
            return obj
        data = _load_json(cls._FILE)
        data.pop("_FILE", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Colores del editor LaTeX
# ---------------------------------------------------------------------------

@dataclass
class LatexEditorColors:
    """Colores para el resaltado de sintaxis LaTeX."""
    command: str           = "#89b4fa"   # \comando
    command_bold: bool     = False
    environment: str       = "#fab387"   # \begin{} \end{}
    environment_bold: bool = True
    math: str              = "#89dceb"   # $...$
    comment: str           = "#6c7086"   # % comentario
    comment_italic: bool   = True
    braces: str            = "#f5c2e7"   # { }
    brackets: str          = "#f9e2af"   # [ ]
    special: str           = "#cba6f7"   # & ^ _ ~

    _FILE = EDITOR_COLORS_FOLDER / "latex_editor.json"

    def save(self):
        _save_json(self._FILE, asdict(self))

    @classmethod
    def load(cls) -> LatexEditorColors:
        if not cls._FILE.exists():
            obj = cls()
            obj.save()
            return obj
        data = _load_json(cls._FILE)
        data.pop("_FILE", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Colores del editor HTML
# ---------------------------------------------------------------------------

@dataclass
class HtmlEditorColors:
    """Colores para el resaltado de sintaxis HTML."""
    tag_name: str          = "#89b4fa"   # div, span, p
    tag_bracket: str       = "#585b70"   # < >
    attribute: str         = "#f9e2af"   # class, id, href
    value: str             = "#a6e3a1"   # "valor"
    comment: str           = "#6c7086"   # <!-- ... -->
    comment_italic: bool   = True
    doctype: str           = "#f38ba8"   # <!DOCTYPE>
    entity: str            = "#fab387"   # &amp; &lt;
    script_style: str      = "#cba6f7"   # contenido de <script>/<style>

    _FILE = EDITOR_COLORS_FOLDER / "html_editor.json"

    def save(self):
        _save_json(self._FILE, asdict(self))

    @classmethod
    def load(cls) -> HtmlEditorColors:
        if not cls._FILE.exists():
            obj = cls()
            obj.save()
            return obj
        data = _load_json(cls._FILE)
        data.pop("_FILE", None)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Carga conjunta al inicio
# ---------------------------------------------------------------------------

def load_all_editor_colors() -> tuple[MdEditorColors, LatexEditorColors, HtmlEditorColors]:
    """Carga (o crea) los tres ficheros de colores de editor."""
    return MdEditorColors.load(), LatexEditorColors.load(), HtmlEditorColors.load()
