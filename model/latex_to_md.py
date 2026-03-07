"""Conversor de LaTeX a Markdown."""

import re


class LatexToMdConverter:
    """Convierte texto LaTeX a Markdown."""

    def convert(self, latex_text: str) -> str:
        text = latex_text

        # Eliminar preámbulo/documento si existe
        text = self._strip_document(text)

        # Entornos de bloque (orden importa: de más específico a más general)
        text = self._convert_lstlisting(text)
        text = self._convert_verbatim(text)
        text = self._convert_tables(text)
        text = self._convert_lists(text)
        text = self._convert_quote(text)

        # Secciones
        text = re.sub(r"\\section\*?\{([^}]*)\}", r"# \1", text)
        text = re.sub(r"\\subsection\*?\{([^}]*)\}", r"## \1", text)
        text = re.sub(r"\\subsubsection\*?\{([^}]*)\}", r"### \1", text)
        text = re.sub(r"\\paragraph\*?\{([^}]*)\}", r"#### \1", text)
        text = re.sub(r"\\subparagraph\*?\{([^}]*)\}", r"##### \1", text)

        # Negrita + itálica
        text = re.sub(r"\\textbf\{\\textit\{([^}]*)\}\}", r"***\1***", text)
        text = re.sub(r"\\textit\{\\textbf\{([^}]*)\}\}", r"***\1***", text)
        # Negrita
        text = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", text)
        # Itálica
        text = re.sub(r"\\textit\{([^}]*)\}", r"*\1*", text)
        text = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", text)
        # Código inline
        text = re.sub(r"\\texttt\{([^}]*)\}", r"`\1`", text)
        # Tachado
        text = re.sub(r"\\sout\{([^}]*)\}", r"~~\1~~", text)

        # Imagen
        text = re.sub(r"\\includegraphics(?:\[.*?\])?\{([^}]*)\}", r"![image](\1)", text)
        # Enlace
        text = re.sub(r"\\href\{([^}]*)\}\{([^}]*)\}", r"[\2](\1)", text)
        text = re.sub(r"\\url\{([^}]*)\}", r"[\1](\1)", text)

        # Línea horizontal
        text = re.sub(r"\\hrule", "---", text)
        text = re.sub(r"\\hline", "", text)

        # Saltos de línea LaTeX
        text = re.sub(r"\\\\", "\n", text)
        text = re.sub(r"\\newline", "\n", text)
        text = re.sub(r"\\par\b", "\n\n", text)

        # Caracteres especiales escapados
        text = text.replace("\\&", "&")
        text = text.replace("\\%", "%")
        text = text.replace("\\$", "$")
        text = text.replace("\\#", "#")
        text = text.replace("\\^{}", "^")
        text = text.replace("\\textasciitilde{}", "~")
        text = text.replace("\\textasciitilde", "~")
        text = re.sub(r"\\LaTeX\b", "LaTeX", text)
        text = re.sub(r"\\TeX\b", "TeX", text)

        # Comandos sin argumento comunes
        text = re.sub(r"\\noindent\b\s*", "", text)
        text = re.sub(r"\\centering\b\s*", "", text)
        text = re.sub(r"\\clearpage\b\s*", "\n", text)
        text = re.sub(r"\\newpage\b\s*", "\n", text)

        # Limpiar comentarios LaTeX
        text = re.sub(r"(?<!\\)%.*", "", text)

        # Limpiar llaves sueltas que queden
        text = re.sub(r"\\begin\{[^}]*\}|\\end\{[^}]*\}", "", text)

        # Normalizar espacios en blanco múltiples
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _strip_document(self, text: str) -> str:
        """Extrae el contenido del entorno document si existe."""
        match = re.search(
            r"\\begin\{document\}(.*?)\\end\{document\}", text, re.DOTALL
        )
        if match:
            return match.group(1).strip()
        # Quitar preámbulo (todo antes de \begin{document} si no hay entorno)
        text = re.sub(r"\\documentclass\{[^}]*\}", "", text)
        text = re.sub(r"\\usepackage(?:\[.*?\])?\{[^}]*\}", "", text)
        text = re.sub(r"\\title\{[^}]*\}", "", text)
        text = re.sub(r"\\author\{[^}]*\}", "", text)
        text = re.sub(r"\\date\{[^}]*\}", "", text)
        text = re.sub(r"\\maketitle\b", "", text)
        return text

    def _convert_lstlisting(self, text: str) -> str:
        def replace(m):
            opts = m.group(1) or ""
            body = m.group(2)
            lang_match = re.search(r"language=(\w+)", opts)
            lang = lang_match.group(1).lower() if lang_match else ""
            return f"```{lang}\n{body}\n```"

        text = re.sub(
            r"\\begin\{lstlisting\}(?:\[(.*?)\])?(.*?)\\end\{lstlisting\}",
            replace,
            text,
            flags=re.DOTALL,
        )
        return text

    def _convert_verbatim(self, text: str) -> str:
        def replace(m):
            body = m.group(1)
            return f"```\n{body}\n```"

        text = re.sub(
            r"\\begin\{verbatim\}(.*?)\\end\{verbatim\}",
            replace,
            text,
            flags=re.DOTALL,
        )
        return text

    def _convert_lists(self, text: str) -> str:
        # Listas anidadas: procesamos de dentro hacia afuera
        for _ in range(4):
            text = re.sub(
                r"\\begin\{itemize\}(.*?)\\end\{itemize\}",
                self._itemize_to_md,
                text,
                flags=re.DOTALL,
            )
            text = re.sub(
                r"\\begin\{enumerate\}(.*?)\\end\{enumerate\}",
                self._enumerate_to_md,
                text,
                flags=re.DOTALL,
            )
        return text

    def _itemize_to_md(self, m: re.Match) -> str:
        body = m.group(1)
        items = re.split(r"\\item\s*", body)
        lines = []
        for item in items:
            item = item.strip()
            if item:
                lines.append(f"- {item}")
        return "\n".join(lines)

    def _enumerate_to_md(self, m: re.Match) -> str:
        body = m.group(1)
        items = re.split(r"\\item\s*", body)
        lines = []
        n = 1
        for item in items:
            item = item.strip()
            if item:
                lines.append(f"{n}. {item}")
                n += 1
        return "\n".join(lines)

    def _convert_quote(self, text: str) -> str:
        def replace(m):
            body = m.group(1).strip()
            lines = body.split("\n")
            return "\n".join(f"> {l}" for l in lines)

        return re.sub(
            r"\\begin\{quote\}(.*?)\\end\{quote\}",
            replace,
            text,
            flags=re.DOTALL,
        )

    def _convert_tables(self, text: str) -> str:
        def replace(m):
            body = m.group(1).strip()
            # Quitar \hline
            body = re.sub(r"\\hline\s*", "", body)
            rows_raw = [r.strip() for r in body.split("\\\\") if r.strip()]
            rows = []
            for row in rows_raw:
                cells = [c.strip() for c in row.split("&")]
                rows.append(cells)
            if not rows:
                return ""
            header = "| " + " | ".join(rows[0]) + " |"
            separator = "| " + " | ".join(["---"] * len(rows[0])) + " |"
            data_rows = [
                "| " + " | ".join(row) + " |" for row in rows[1:]
            ]
            return "\n".join([header, separator] + data_rows)

        return re.sub(
            r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}",
            replace,
            text,
            flags=re.DOTALL,
        )
