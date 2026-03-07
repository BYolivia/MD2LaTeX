"""Modelo de configuración de colores por lenguaje para lstlisting."""

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
    """Configuración completa de colores para un lenguaje."""

    language: str
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
    # Mostrar color de identificadores solo si el usuario lo activa
    use_identifier_color: bool = False

    # ------------------------------------------------------------------
    # Derivados
    # ------------------------------------------------------------------

    def style_name(self) -> str:
        return f"{self.language.lower().replace(' ', '_')}_colors"

    def to_latex(self) -> str:
        """Genera el bloque \\lstdefinestyle para este config."""
        lines = [f"\\lstdefinestyle{{{self.style_name()}}}{{"]
        lines.append(f"  keywordstyle={self.keywords.to_latex()},")
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
            "keywords": asdict(self.keywords),
            "comments": asdict(self.comments),
            "strings": asdict(self.strings),
            "identifiers": asdict(self.identifiers),
            "use_background": self.use_background,
            "background_color": self.background_color,
            "font_size": self.font_size,
            "use_identifier_color": self.use_identifier_color,
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> LanguageColorConfig:
        """Carga desde un archivo JSON."""
        data = json.loads(path.read_text(encoding="utf-8"))
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

_DEFAULTS: list[LanguageColorConfig] = [
    LanguageColorConfig(
        language="python",
        keywords=ElementStyle("#0055CC", bold=True),
        comments=ElementStyle("#408040", italic=True),
        strings=ElementStyle("#BB4400"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="javascript",
        keywords=ElementStyle("#0000BB", bold=True),
        comments=ElementStyle("#777777", italic=True),
        strings=ElementStyle("#DD4400"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="bash",
        keywords=ElementStyle("#005588", bold=True),
        comments=ElementStyle("#228B22", italic=True),
        strings=ElementStyle("#8B0000"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="typescript",
        keywords=ElementStyle("#0000BB", bold=True),
        comments=ElementStyle("#777777", italic=True),
        strings=ElementStyle("#DD4400"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="go",
        keywords=ElementStyle("#006699", bold=True),
        comments=ElementStyle("#666666", italic=True),
        strings=ElementStyle("#CC4400"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="rust",
        keywords=ElementStyle("#7C3AED", bold=True),
        comments=ElementStyle("#6B7280", italic=True),
        strings=ElementStyle("#DC2626"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="java",
        keywords=ElementStyle("#7400B8", bold=True),
        comments=ElementStyle("#3D7A00", italic=True),
        strings=ElementStyle("#BC0000"),
        font_size="small",
    ),
    LanguageColorConfig(
        language="sql",
        keywords=ElementStyle("#AA0000", bold=True),
        comments=ElementStyle("#338800", italic=True),
        strings=ElementStyle("#004488"),
        font_size="small",
    ),
]


def create_default_configs(folder: Path = COLORS_FOLDER):
    """Crea los archivos JSON por defecto si la carpeta no existe."""
    if folder.exists() and any(folder.glob("*.json")):
        return
    for cfg in _DEFAULTS:
        cfg.save(folder)
