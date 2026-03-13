"""Modelo de configuración de colores y sintaxis por lenguaje para lstlisting."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Carpeta donde se guardan los JSON de configuración
COLORS_FOLDER = Path(__file__).parent.parent / "language_colors"

FONT_SIZES = [
    "tiny", "scriptsize", "footnotesize", "small",
    "normalsize", "large", "Large",
]


@dataclass
class ElementStyle:
    """Estilo de un elemento de código (color + negrita/cursiva)."""
    color: str = "#000000"
    bold: bool = False
    italic: bool = False

    def to_latex(self) -> str:
        hex_color = self.color.lstrip("#").upper()
        s = f"\\color[HTML]{{{hex_color}}}"
        if self.bold:
            s += "\\bfseries"
        if self.italic:
            s += "\\itshape"
        return s


@dataclass
class LanguageColorConfig:
    """Configuración completa de colores Y sintaxis para un lenguaje.

    Los campos de sintaxis (keywords_list, keywords2_list, comment_line, etc.)
    determinan qué tokens colorea listings en LaTeX y el resaltador en la GUI.
    """

    language: str

    # ── Estilos de color ─────────────────────────────────────────────────
    keywords: ElementStyle = field(
        default_factory=lambda: ElementStyle("#0055CC", bold=True)
    )
    comments: ElementStyle = field(
        default_factory=lambda: ElementStyle("#558855", italic=True)
    )
    strings: ElementStyle = field(
        default_factory=lambda: ElementStyle("#CC3300")
    )
    identifiers: ElementStyle = field(
        default_factory=lambda: ElementStyle("#000000")
    )
    use_background: bool = False
    background_color: str = "#F8F8F8"
    font_size: str = "small"
    use_identifier_color: bool = False

    # ── Reglas sintácticas ────────────────────────────────────────────────
    # keywords_list  → palabras que lstlisting colorea con keywordstyle[1]
    keywords_list: list[str] = field(default_factory=list)
    # keywords2_list → tipos, built-ins, constantes; coloreados con keywordstyle[2]
    keywords2_list: list[str] = field(default_factory=list)
    # comment_line   → marcadores de comentario de línea (p. ej. ["//", "#"])
    comment_line: list[str] = field(default_factory=list)
    # comment_block  → delimitador de bloque (abre, cierra) o ("", "")
    comment_block_open: str = ""
    comment_block_close: str = ""
    # string_delimiters → caracteres que delimitan cadenas (p. ej. ['"', "'", "`"])
    string_delimiters: list[str] = field(default_factory=lambda: ['"', "'"])
    # case_sensitive → False para SQL y similares
    case_sensitive: bool = True

    # ------------------------------------------------------------------
    # Derivados
    # ------------------------------------------------------------------

    def style_name(self) -> str:
        return f"{self.language.lower().replace(' ', '_')}_colors"

    def to_latex(self) -> str:
        """Genera el bloque LaTeX completo: palabras clave + colores."""
        lines = [f"\\lstdefinestyle{{{self.style_name()}}}{{"]

        # ── Listas explícitas de palabras clave ──
        if self.keywords_list:
            kw_csv = ",".join(self.keywords_list)
            lines.append(f"  morekeywords={{[1]{{{kw_csv}}}}},")

        if self.keywords2_list:
            kw2_csv = ",".join(self.keywords2_list)
            lines.append(f"  morekeywords={{[2]{{{kw2_csv}}}}},")

        # ── Estilos de color ──
        kw_latex = self.keywords.to_latex()
        lines.append(f"  keywordstyle={{[1]{kw_latex}}},")

        if self.keywords2_list:
            kw2_style = (
                self.identifiers.to_latex()
                if self.use_identifier_color
                else self.keywords.to_latex()
            )
            lines.append(f"  keywordstyle={{[2]{kw2_style}}},")

        lines.append(f"  commentstyle={self.comments.to_latex()},")
        lines.append(f"  stringstyle={self.strings.to_latex()},")

        if self.use_identifier_color:
            lines.append(f"  identifierstyle={self.identifiers.to_latex()},")

        if self.use_background:
            hex_bg = self.background_color.lstrip("#").upper()
            lines.append(f"  backgroundcolor=\\color[HTML]{{{hex_bg}}},")

        lines.append(f"  basicstyle=\\ttfamily\\{self.font_size},")
        lines.append("}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    def save(self, folder: Path = COLORS_FOLDER) -> Path:
        """Guarda la configuración en un archivo JSON. Devuelve la ruta."""
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{self.language.lower()}.json"
        data = {
            "language": self.language,
            "keywords":    asdict(self.keywords),
            "comments":    asdict(self.comments),
            "strings":     asdict(self.strings),
            "identifiers": asdict(self.identifiers),
            "use_background":     self.use_background,
            "background_color":   self.background_color,
            "font_size":          self.font_size,
            "use_identifier_color": self.use_identifier_color,
            # Reglas sintácticas
            "keywords_list":       self.keywords_list,
            "keywords2_list":      self.keywords2_list,
            "comment_line":        self.comment_line,
            "comment_block_open":  self.comment_block_open,
            "comment_block_close": self.comment_block_close,
            "string_delimiters":   self.string_delimiters,
            "case_sensitive":      self.case_sensitive,
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> LanguageColorConfig:
        """Carga desde un archivo JSON.

        Si el JSON no tiene los campos de sintaxis (formato antiguo),
        los rellena automáticamente desde language_syntax.py como valores
        por defecto.
        """
        data = json.loads(path.read_text(encoding="utf-8"))
        lang_key = data.get("language", "").lower()

        # Valores por defecto de sintaxis desde language_syntax
        from model.language_syntax import get_syntax
        syntax = get_syntax(lang_key)

        def _get(json_key, syntax_attr, fallback):
            """Devuelve: valor del JSON si no está vacío; si no, atributo de syntax; si no, fallback."""
            value = data.get(json_key)
            if value is None or value == [] or value == "":
                return getattr(syntax, syntax_attr, fallback) if syntax else fallback
            return value

        # Comentario de bloque (par open/close)
        cb_open  = data.get("comment_block_open", "")
        cb_close = data.get("comment_block_close", "")
        if (not cb_open) and syntax and syntax.comment_block:
            cb_open, cb_close = syntax.comment_block

        return cls(
            language=data["language"],
            keywords=ElementStyle(**data["keywords"]),
            comments=ElementStyle(**data["comments"]),
            strings=ElementStyle(**data["strings"]),
            identifiers=ElementStyle(**data.get("identifiers", {})),
            use_background=data.get("use_background", False),
            background_color=data.get("background_color", "#F8F8F8"),
            font_size=data.get("font_size", "small"),
            use_identifier_color=data.get("use_identifier_color", False),
            # Sintaxis — campo JSON → atributo LanguageSyntax → fallback
            keywords_list=    _get("keywords_list",    "keywords",          []),
            keywords2_list=   _get("keywords2_list",   "keywords2",         []),
            comment_line=     _get("comment_line",     "comment_line",      []),
            comment_block_open=cb_open,
            comment_block_close=cb_close,
            string_delimiters=_get("string_delimiters","string_delimiters", ['"', "'"]),
            case_sensitive=   _get("case_sensitive",   "case_sensitive",    True),
        )

    @classmethod
    def load_all(cls, folder: Path = COLORS_FOLDER) -> dict[str, LanguageColorConfig]:
        """Carga todos los JSON de la carpeta. Clave = nombre normalizado."""
        if not folder.exists():
            return {}
        configs: dict[str, LanguageColorConfig] = {}
        for json_file in sorted(folder.glob("*.json")):
            try:
                cfg = cls.load(json_file)
                configs[cfg.language.lower()] = cfg
            except Exception:
                pass
        return configs

    @classmethod
    def delete(cls, language: str, folder: Path = COLORS_FOLDER) -> bool:
        """Elimina el JSON de un lenguaje. Devuelve True si existía."""
        path = folder / f"{language.lower()}.json"
        if path.exists():
            path.unlink()
            return True
        return False


# ---------------------------------------------------------------------------
# Configs por defecto para lenguajes comunes
# ---------------------------------------------------------------------------

def _make_default(
    language: str,
    kw_color: str,
    cm_color: str,
    st_color: str,
    id_color: str = "#DCDCAA",
    kw_bold: bool = True,
    cm_italic: bool = True,
    use_id: bool = True,
) -> LanguageColorConfig:
    """Crea un LanguageColorConfig con colores dados y sintaxis desde language_syntax."""
    from model.language_syntax import get_syntax
    syntax = get_syntax(language)

    cb_open = cb_close = ""
    if syntax and syntax.comment_block:
        cb_open, cb_close = syntax.comment_block

    return LanguageColorConfig(
        language=language,
        keywords=ElementStyle(kw_color, bold=kw_bold),
        comments=ElementStyle(cm_color, italic=cm_italic),
        strings=ElementStyle(st_color),
        identifiers=ElementStyle(id_color),
        use_identifier_color=use_id,
        font_size="small",
        keywords_list=syntax.keywords if syntax else [],
        keywords2_list=syntax.keywords2 if syntax else [],
        comment_line=syntax.comment_line if syntax else [],
        comment_block_open=cb_open,
        comment_block_close=cb_close,
        string_delimiters=syntax.string_delimiters if syntax else ['"', "'"],
        case_sensitive=syntax.case_sensitive if syntax else True,
    )


# Paleta inspirada en VS Code Dark+:
#   kw  = palabras clave (control flow)  → azul o naranja/ámbar
#   kw2 = tipos / built-ins              → dorado o teal
#   cm  = comentarios                    → verde
#   st  = cadenas                        → cobre/salmón
_DEFAULTS: list[LanguageColorConfig] = [
    _make_default("python",     "#569CD6", "#6A9955", "#CE9178", id_color="#DCDCAA"),
    _make_default("javascript", "#569CD6", "#6A9955", "#CE9178", id_color="#DCDCAA"),
    _make_default("typescript", "#569CD6", "#6A9955", "#CE9178", id_color="#4EC9B0"),
    _make_default("java",       "#CC7832", "#629755", "#6A8759", id_color="#4EC9B0"),
    _make_default("go",         "#CC7832", "#6A9955", "#CE9178", id_color="#4EC9B0"),
    _make_default("rust",       "#569CD6", "#6A9955", "#CE9178", id_color="#4EC9B0"),
    _make_default("sql",        "#CC7832", "#6A9955", "#CE9178", id_color="#569CD6"),
    _make_default("bash",       "#569CD6", "#6A9955", "#CE9178", id_color="#DCDCAA"),
]


def create_default_configs(folder: Path = COLORS_FOLDER):
    """Crea los archivos JSON por defecto si la carpeta no existe."""
    if folder.exists() and any(folder.glob("*.json")):
        return
    for cfg in _DEFAULTS:
        cfg.save(folder)
