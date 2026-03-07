"""Conversor de Markdown a LaTeX."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from model.latex_languages import resolve_language, build_preamble


@dataclass
class ConversionResult:
    """Resultado de una conversión MD → LaTeX."""
    body: str
    preamble_imports: str  # \usepackage{...} – va al inicio del preámbulo
    preamble_config: str   # \lstset, \lstdefinelanguage, \lstdefinestyle – va después
    languages: set[str] = field(default_factory=set)


class MdToLatexConverter:
    """Convierte texto Markdown a LaTeX."""

    def convert(self, md_text: str, color_configs: dict | None = None) -> ConversionResult:
        self._languages: set[str] = set()
        self._color_configs = color_configs or {}
        lines = md_text.split("\n")
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Bloque de código con triple backtick
            if line.startswith("```"):
                lang_md = line[3:].strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                code_body = "\n".join(code_lines)
                result.append(self._lstlisting_block(lang_md, code_body))
                i += 1
                continue

            # Lista no ordenada
            if re.match(r"^(\s*)[*\-+] ", line):
                block = []
                while i < len(lines) and re.match(r"^(\s*)[*\-+] ", lines[i]):
                    item_text = re.sub(r"^\s*[*\-+] ", "", lines[i])
                    block.append(self._inline(item_text))
                    i += 1
                result.append("\\begin{itemize}")
                for item in block:
                    result.append(f"  \\item {item}")
                result.append("\\end{itemize}")
                continue

            # Lista ordenada
            if re.match(r"^\s*\d+\. ", line):
                block = []
                while i < len(lines) and re.match(r"^\s*\d+\. ", lines[i]):
                    item_text = re.sub(r"^\s*\d+\. ", "", lines[i])
                    block.append(self._inline(item_text))
                    i += 1
                result.append("\\begin{enumerate}")
                for item in block:
                    result.append(f"  \\item {item}")
                result.append("\\end{enumerate}")
                continue

            # Blockquote
            if line.startswith("> "):
                block = []
                while i < len(lines) and lines[i].startswith("> "):
                    block.append(self._inline(lines[i][2:]))
                    i += 1
                result.append("\\begin{quote}")
                result.extend(block)
                result.append("\\end{quote}")
                continue

            # Tabla Markdown
            if "|" in line and i + 1 < len(lines) and re.match(r"^\|?[\s\-|:]+\|?$", lines[i + 1]):
                headers = [h.strip() for h in line.strip().strip("|").split("|")]
                i += 2  # saltar línea de separación
                rows = []
                while i < len(lines) and "|" in lines[i]:
                    row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append(row)
                    i += 1
                col_fmt = "|".join(["c"] * len(headers))
                result.append(f"\\begin{{tabular}}{{|{col_fmt}|}}")
                result.append("\\hline")
                result.append(" & ".join(self._inline(h) for h in headers) + " \\\\")
                result.append("\\hline")
                for row in rows:
                    result.append(" & ".join(self._inline(c) for c in row) + " \\\\")
                result.append("\\hline")
                result.append("\\end{tabular}")
                continue

            # Línea horizontal
            if re.match(r"^(\s*[-*_]){3,}\s*$", line):
                result.append("\\hrule")
                i += 1
                continue

            # Encabezados
            header_match = re.match(r"^(#{1,6})\s+(.*)", line)
            if header_match:
                level = len(header_match.group(1))
                text = self._inline(header_match.group(2))
                cmds = [
                    "\\section",
                    "\\subsection",
                    "\\subsubsection",
                    "\\paragraph",
                    "\\subparagraph",
                    "\\textbf",
                ]
                cmd = cmds[min(level - 1, 5)]
                result.append(f"{cmd}{{{text}}}")
                i += 1
                continue

            # Línea vacía
            if line.strip() == "":
                result.append("")
                i += 1
                continue

            # Párrafo normal
            result.append(self._inline(line))
            i += 1

        body = "\n".join(result)
        imports, config = build_preamble(self._languages, self._color_configs)
        return ConversionResult(
            body=body,
            preamble_imports=imports,
            preamble_config=config,
            languages=set(self._languages),
        )

    # ------------------------------------------------------------------
    # Bloque lstlisting con resolución de lenguaje
    # ------------------------------------------------------------------

    def _lstlisting_block(self, lang_md: str, code_body: str) -> str:
        if not lang_md:
            return f"\\begin{{lstlisting}}\n{code_body}\n\\end{{lstlisting}}"

        self._languages.add(lang_md)
        info = resolve_language(lang_md)

        opts: list[str] = []
        if info.listings_name:
            opts.append(f"language={info.listings_name}")
        else:
            # Lenguaje desconocido: aviso como comentario LaTeX
            return (
                f"\\begin{{lstlisting}}% lenguaje '{lang_md}' no reconocido\n"
                f"{code_body}\n\\end{{lstlisting}}"
            )

        # Añadir estilo de color si existe config para este lenguaje
        key = lang_md.lower()
        from model.latex_languages import _CUSTOM_ALIASES
        key = _CUSTOM_ALIASES.get(key, key)
        if key in self._color_configs:
            opts.append(f"style={self._color_configs[key].style_name()}")

        header = f"\\begin{{lstlisting}}[{', '.join(opts)}]"
        return f"{header}\n{code_body}\n\\end{{lstlisting}}"

    # ------------------------------------------------------------------
    # Conversión inline
    # ------------------------------------------------------------------

    def _inline(self, text: str) -> str:
        # Negrita e itálica combinadas
        text = re.sub(r"\*\*\*(.*?)\*\*\*", r"\\textbf{\\textit{\1}}", text)
        text = re.sub(r"___(.*?)___", r"\\textbf{\\textit{\1}}", text)
        # Negrita
        text = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", text)
        text = re.sub(r"__(.*?)__", r"\\textbf{\1}", text)
        # Itálica
        text = re.sub(r"\*(.*?)\*", r"\\textit{\1}", text)
        text = re.sub(r"_(.*?)_", r"\\textit{\1}", text)
        # Código inline
        text = re.sub(r"`(.*?)`", r"\\texttt{\1}", text)
        # Tachado
        text = re.sub(r"~~(.*?)~~", r"\\sout{\1}", text)
        # Imagen: ![alt](url)
        text = re.sub(r"!\[(.*?)\]\((.*?)\)", r"\\includegraphics{\2}", text)
        # Enlace: [text](url)
        text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\\href{\2}{\1}", text)
        text = self._escape_special(text)
        return text

    def _escape_special(self, text: str) -> str:
        parts = re.split(r"(\\[a-zA-Z]+\{[^}]*\}|\\[a-zA-Z]+)", text)
        escaped = []
        for part in parts:
            if part.startswith("\\"):
                escaped.append(part)
            else:
                part = part.replace("&", "\\&")
                part = part.replace("%", "\\%")
                part = part.replace("$", "\\$")
                part = part.replace("#", "\\#")
                part = part.replace("^", "\\^{}")
                part = part.replace("~", "\\textasciitilde{}")
                escaped.append(part)
        return "".join(escaped)
