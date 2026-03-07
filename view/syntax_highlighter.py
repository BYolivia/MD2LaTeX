"""Resaltado de sintaxis para los paneles de texto (MD, LaTeX, HTML)."""

from __future__ import annotations

import re
import tkinter as tk

from model.editor_color_config import MdEditorColors, LatexEditorColors, HtmlEditorColors

FONT_MONO = ("Courier New", 11)


# ---------------------------------------------------------------------------
# Clase base
# ---------------------------------------------------------------------------

class _BaseHighlighter:
    """Implementa el patrón de debounce para no resaltar en cada tecla."""

    _DEBOUNCE_MS = 200

    def __init__(self):
        self._debounce_id = None

    def configure_tags(self, widget: tk.Text):
        raise NotImplementedError

    def highlight(self, widget: tk.Text):
        raise NotImplementedError

    def schedule(self, widget: tk.Text):
        if self._debounce_id:
            try:
                widget.after_cancel(self._debounce_id)
            except Exception:
                pass
        self._debounce_id = widget.after(self._DEBOUNCE_MS, lambda: self.highlight(widget))


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

class MdHighlighter(_BaseHighlighter):

    def __init__(self, colors: MdEditorColors):
        super().__init__()
        self._c = colors

    def update_colors(self, colors: MdEditorColors):
        self._c = colors

    def configure_tags(self, widget: tk.Text):
        c = self._c
        bold_w = "bold"
        # Prioridad (mayor = gana): codeblock > inline_code > link > heading
        # > bold > italic > list_marker > quote > hr > strikethrough
        # En tkinter, el tag creado ÚLTIMO tiene mayor prioridad.
        widget.tag_configure("md_strikethrough", foreground=c.strikethrough,
                             font=(*FONT_MONO[:1], FONT_MONO[1], "overstrike"))
        widget.tag_configure("md_hr",         foreground=c.hr_color)
        widget.tag_configure("md_quote",      foreground=c.quote,
                             font=(*FONT_MONO[:1], FONT_MONO[1],
                                   "italic" if c.quote_italic else "normal"))
        widget.tag_configure("md_list_mark",  foreground=c.list_marker)
        widget.tag_configure("md_italic",     foreground=c.italic_text,
                             font=(*FONT_MONO[:1], FONT_MONO[1], "italic"))
        widget.tag_configure("md_bold",       foreground=c.bold_text,
                             font=(*FONT_MONO[:1], FONT_MONO[1], "bold"))
        widget.tag_configure("md_heading",    foreground=c.heading,
                             font=(*FONT_MONO[:1], 12, "bold" if c.heading_bold else "normal"))
        widget.tag_configure("md_link",       foreground=c.link)
        widget.tag_configure("md_code",       foreground=c.inline_code,
                             background=c.inline_code_bg,
                             font=("Courier New", 11))
        widget.tag_configure("md_codeblock",  foreground=c.code_block,
                             background=c.code_block_bg)

    def highlight(self, widget: tk.Text):
        all_tags = (
            "md_strikethrough", "md_hr", "md_quote", "md_list_mark",
            "md_italic", "md_bold", "md_heading", "md_link",
            "md_code", "md_codeblock",
        )
        for tag in all_tags:
            widget.tag_remove(tag, "1.0", tk.END)

        content = widget.get("1.0", tk.END)
        lines = content.split("\n")
        in_code_block = False

        for i, line in enumerate(lines):
            ln = i + 1
            s = f"{ln}.0"
            e = f"{ln}.end"

            # Bloque de código (triple backtick)
            if line.startswith("```"):
                in_code_block = not in_code_block
                widget.tag_add("md_codeblock", s, e)
                continue
            if in_code_block:
                widget.tag_add("md_codeblock", s, e)
                continue

            # Encabezados
            if re.match(r"^#{1,6}\s", line):
                widget.tag_add("md_heading", s, e)
                continue

            # Cita
            if line.startswith("> "):
                widget.tag_add("md_quote", s, e)
                continue

            # Línea horizontal
            if re.match(r"^(\s*[-*_]){3,}\s*$", line):
                widget.tag_add("md_hr", s, e)
                continue

            # Marcadores de lista
            for m in re.finditer(r"^(\s*[*\-+]|\s*\d+\.)\s", line):
                widget.tag_add("md_list_mark", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Tachado ~~...~~
            for m in re.finditer(r"~~[^~\n]+~~", line):
                widget.tag_add("md_strikethrough", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Negrita+cursiva ***...***
            for m in re.finditer(r"\*{3}[^*\n]+\*{3}", line):
                widget.tag_add("md_bold", f"{ln}.{m.start()}", f"{ln}.{m.end()}")
                widget.tag_add("md_italic", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Negrita **...**
            for m in re.finditer(r"\*\*[^*\n]+\*\*|__[^_\n]+__", line):
                widget.tag_add("md_bold", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Cursiva *...*
            for m in re.finditer(r"(?<!\*)\*[^*\n]+\*(?!\*)|(?<!_)_[^_\n]+_(?!_)", line):
                widget.tag_add("md_italic", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Código inline `...`
            for m in re.finditer(r"`[^`\n]+`", line):
                widget.tag_add("md_code", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Enlace/imagen [...](...)
            for m in re.finditer(r"!?\[[^\]\n]*\]\([^\)\n]*\)", line):
                widget.tag_add("md_link", f"{ln}.{m.start()}", f"{ln}.{m.end()}")


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

class LatexHighlighter(_BaseHighlighter):

    def __init__(self, colors: LatexEditorColors):
        super().__init__()
        self._c = colors

    def update_colors(self, colors: LatexEditorColors):
        self._c = colors

    def configure_tags(self, widget: tk.Text):
        c = self._c
        # Prioridad (último = más alto): comment > environment > math > cmd > special > brace/bracket
        widget.tag_configure("ltx_bracket",  foreground=c.brackets)
        widget.tag_configure("ltx_brace",    foreground=c.braces)
        widget.tag_configure("ltx_special",  foreground=c.special)
        widget.tag_configure("ltx_cmd",      foreground=c.command,
                             font=(*FONT_MONO[:1], FONT_MONO[1],
                                   "bold" if c.command_bold else "normal"))
        widget.tag_configure("ltx_math",     foreground=c.math)
        widget.tag_configure("ltx_env",      foreground=c.environment,
                             font=(*FONT_MONO[:1], FONT_MONO[1],
                                   "bold" if c.environment_bold else "normal"))
        widget.tag_configure("ltx_comment",  foreground=c.comment,
                             font=(*FONT_MONO[:1], FONT_MONO[1],
                                   "italic" if c.comment_italic else "normal"))

    def highlight(self, widget: tk.Text):
        all_tags = ("ltx_bracket", "ltx_brace", "ltx_special",
                    "ltx_cmd", "ltx_math", "ltx_env", "ltx_comment")
        for tag in all_tags:
            widget.tag_remove(tag, "1.0", tk.END)

        content = widget.get("1.0", tk.END)
        lines = content.split("\n")

        for i, line in enumerate(lines):
            ln = i + 1

            # Comentarios LaTeX (% no escapado) — se aplican al final para tener prioridad
            comment_start = None
            m = re.search(r"(?<!\\)%", line)
            if m:
                comment_start = m.start()
                effective_line = line[:comment_start]
            else:
                effective_line = line

            # Entornos \begin{} y \end{} (mayor prioridad sobre \cmd)
            for m in re.finditer(r"\\(?:begin|end)\{[^}]*\}", effective_line):
                widget.tag_add("ltx_env", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Comandos \palabra
            for m in re.finditer(r"\\[a-zA-Z@]+\*?", effective_line):
                widget.tag_add("ltx_cmd", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Matemáticas $...$
            for m in re.finditer(r"\$[^$\n]*\$", effective_line):
                widget.tag_add("ltx_math", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Caracteres especiales & ^ _ ~ (fuera de comandos)
            for m in re.finditer(r"(?<!\\)[&^_~]", effective_line):
                widget.tag_add("ltx_special", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Llaves { }
            for m in re.finditer(r"(?<!\\)[{}]", effective_line):
                widget.tag_add("ltx_brace", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Corchetes [ ]
            for m in re.finditer(r"[\[\]]", effective_line):
                widget.tag_add("ltx_bracket", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Comentario al final de la línea
            if comment_start is not None:
                widget.tag_add("ltx_comment", f"{ln}.{comment_start}", f"{ln}.end")


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

class HtmlHighlighter(_BaseHighlighter):

    def __init__(self, colors: HtmlEditorColors):
        super().__init__()
        self._c = colors

    def update_colors(self, colors: HtmlEditorColors):
        self._c = colors

    def configure_tags(self, widget: tk.Text):
        c = self._c
        # Prioridad (último = más alto): comment > doctype > script_style > value > attr > tag_name > bracket
        widget.tag_configure("html_bracket",      foreground=c.tag_bracket)
        widget.tag_configure("html_entity",       foreground=c.entity)
        widget.tag_configure("html_tag_name",     foreground=c.tag_name)
        widget.tag_configure("html_attr",         foreground=c.attribute)
        widget.tag_configure("html_value",        foreground=c.value)
        widget.tag_configure("html_script_style", foreground=c.script_style)
        widget.tag_configure("html_doctype",      foreground=c.doctype)
        widget.tag_configure("html_comment",      foreground=c.comment,
                             font=(*FONT_MONO[:1], FONT_MONO[1],
                                   "italic" if c.comment_italic else "normal"))

    def highlight(self, widget: tk.Text):
        all_tags = ("html_bracket", "html_entity", "html_tag_name",
                    "html_attr", "html_value", "html_script_style",
                    "html_doctype", "html_comment")
        for tag in all_tags:
            widget.tag_remove(tag, "1.0", tk.END)

        content = widget.get("1.0", tk.END)

        def tag_range(tag_name, start_char, end_char):
            """Aplica un tag a una región del contenido completo."""
            start_idx = self._pos_to_index(content, start_char)
            end_idx   = self._pos_to_index(content, end_char)
            widget.tag_add(tag_name, start_idx, end_idx)

        # Comentarios <!-- ... -->
        for m in re.finditer(r"<!--.*?-->", content, re.DOTALL):
            tag_range("html_comment", m.start(), m.end())

        # DOCTYPE
        for m in re.finditer(r"<!DOCTYPE[^>]*>", content, re.IGNORECASE):
            tag_range("html_doctype", m.start(), m.end())

        # Etiquetas completas <tag attr="val">
        for m in re.finditer(r"</?[a-zA-Z][^>]*>", content):
            tag_text = m.group()
            base = m.start()

            # Ángulos < >
            tag_range("html_bracket", base, base + 1)
            tag_range("html_bracket", base + len(tag_text) - 1, base + len(tag_text))

            # Nombre de etiqueta
            name_m = re.match(r"</?([a-zA-Z][a-zA-Z0-9\-]*)", tag_text)
            if name_m:
                tag_range("html_tag_name",
                          base + name_m.start(1), base + name_m.end(1))

            # Atributos y valores dentro de la etiqueta
            inner = tag_text[name_m.end() if name_m else 1 : -1]
            inner_base = base + (name_m.end() if name_m else 1)

            for am in re.finditer(r'([a-zA-Z\-:]+)\s*=\s*("[^"]*"|\'[^\']*\')', inner):
                tag_range("html_attr",
                          inner_base + am.start(1), inner_base + am.end(1))
                tag_range("html_value",
                          inner_base + am.start(2), inner_base + am.end(2))

        # Entidades &...;
        for m in re.finditer(r"&[a-zA-Z#0-9]+;", content):
            tag_range("html_entity", m.start(), m.end())

        # Contenido de <script> y <style>
        for m in re.finditer(
            r"<(script|style)[^>]*>(.*?)</(script|style)>",
            content, re.DOTALL | re.IGNORECASE
        ):
            tag_range("html_script_style", m.start(2), m.end(2))

    @staticmethod
    def _pos_to_index(content: str, char_pos: int) -> str:
        """Convierte un offset de carácter a índice tkinter 'línea.col'."""
        before = content[:char_pos]
        line = before.count("\n") + 1
        col  = char_pos - before.rfind("\n") - 1
        return f"{line}.{col}"
