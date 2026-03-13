"""Resaltado de sintaxis para los paneles de texto (MD, LaTeX, HTML)."""

from __future__ import annotations

import re
import tkinter as tk

from model.editor_color_config import MdEditorColors, LatexEditorColors, HtmlEditorColors

FONT_MONO = ("Courier New", 11)


# ---------------------------------------------------------------------------
# Helpers internos para resaltado de bloques de código
# ---------------------------------------------------------------------------

def _make_font(bold: bool, italic: bool) -> tuple:
    styles = []
    if bold:
        styles.append("bold")
    if italic:
        styles.append("italic")
    return ("Courier New", 11, " ".join(styles)) if styles else ("Courier New", 11)


def _find_string_ranges(line: str, delimiters: list[str]) -> list[tuple[int, int]]:
    """Detecta todos los rangos de cadenas de texto en una línea."""
    ranges: list[tuple[int, int]] = []
    i = 0
    while i < len(line):
        matched = False
        for delim in sorted(delimiters, key=len, reverse=True):
            if line[i:i + len(delim)] == delim:
                j = i + len(delim)
                while j < len(line):
                    if line[j] == '\\':
                        j += 2
                        continue
                    if line[j:j + len(delim)] == delim:
                        ranges.append((i, j + len(delim)))
                        i = j + len(delim)
                        matched = True
                        break
                    j += 1
                else:
                    # Cadena sin cerrar: llega al final de la línea
                    ranges.append((i, len(line)))
                    i = len(line)
                    matched = True
                break
        if not matched:
            i += 1
    return ranges


def _find_comment_start(
    line: str,
    markers: list[str],
    string_ranges: list[tuple[int, int]],
) -> int | None:
    """Devuelve la posición del primer marcador de comentario de línea, o None."""
    best: int | None = None
    for marker in markers:
        pos = 0
        while True:
            idx = line.find(marker, pos)
            if idx == -1:
                break
            if not any(s <= idx < e for s, e in string_ranges):
                if best is None or idx < best:
                    best = idx
                break
            pos = idx + len(marker)
    return best


# ---------------------------------------------------------------------------
# Resaltador de bloques de código (usado por MdHighlighter y LatexHighlighter)
# ---------------------------------------------------------------------------

class _CodeHighlighter:
    """
    Aplica resaltado de sintaxis a bloques de código dentro de un tk.Text.

    Usa:
      - model.language_syntax.LanguageSyntax  →  qué palabras son keywords
      - model.language_color_config.LanguageColorConfig  →  qué colores aplicar
    """

    def __init__(self, color_configs: dict):
        """
        Args:
            color_configs: dict {lang_key: LanguageColorConfig}
        """
        self._configs = color_configs

    def update_configs(self, configs: dict) -> None:
        self._configs = configs

    # ------------------------------------------------------------------
    # Nombre de tags por lenguaje
    # ------------------------------------------------------------------

    @staticmethod
    def _tag(lang_key: str, kind: str) -> str:
        return f"cb_{lang_key}_{kind}"

    # ------------------------------------------------------------------
    # Configurar tags (llamar una vez al crear/actualizar colores)
    # ------------------------------------------------------------------

    def configure_tags(self, widget: tk.Text) -> None:
        """Registra todos los tags de colores de código en el widget."""
        for lang_key, cfg in self._configs.items():
            widget.tag_configure(
                self._tag(lang_key, "kw"),
                foreground=cfg.keywords.color,
                font=_make_font(cfg.keywords.bold, cfg.keywords.italic),
            )
            # kw2: si use_identifier_color=True usa identifiers, si no usa keywords
            # (igual que to_latex() para evitar que #000000 sea invisible sobre fondo oscuro)
            kw2_style = cfg.identifiers if cfg.use_identifier_color else cfg.keywords
            widget.tag_configure(
                self._tag(lang_key, "kw2"),
                foreground=kw2_style.color,
                font=_make_font(kw2_style.bold, kw2_style.italic),
            )
            widget.tag_configure(
                self._tag(lang_key, "cm"),
                foreground=cfg.comments.color,
                font=_make_font(cfg.comments.bold, cfg.comments.italic),
            )
            widget.tag_configure(
                self._tag(lang_key, "st"),
                foreground=cfg.strings.color,
                font=_make_font(cfg.strings.bold, cfg.strings.italic),
            )

    # ------------------------------------------------------------------
    # Borrar tags de código en un rango
    # ------------------------------------------------------------------

    def remove_tags_in_range(self, widget: tk.Text,
                              start: str, end: str) -> None:
        for lang_key in self._configs:
            for kind in ("kw", "kw2", "cm", "st"):
                widget.tag_remove(self._tag(lang_key, kind), start, end)

    # ------------------------------------------------------------------
    # Resaltar un bloque (líneas start_ln … end_ln, inclusive)
    # ------------------------------------------------------------------

    def highlight_block(self, widget: tk.Text,
                        start_ln: int, end_ln: int,
                        lang: str) -> None:
        """Resalta las líneas [start_ln, end_ln] con los colores del JSON."""
        from model.language_syntax import normalize_lang

        lang_key = normalize_lang(lang)
        cfg = self._configs.get(lang_key)
        if not cfg:
            return

        tag_kw = self._tag(lang_key, "kw")
        tag_kw2 = self._tag(lang_key, "kw2")
        tag_cm = self._tag(lang_key, "cm")
        tag_st = self._tag(lang_key, "st")

        kw_set = set(cfg.keywords_list)
        kw2_set = set(cfg.keywords2_list)
        case_sensitive = cfg.case_sensitive

        # Para SQL u otros lenguajes case-insensitive usamos comparación en mayúsc.
        if not case_sensitive:
            kw_upper = {k.upper() for k in kw_set}
            kw2_upper = {k.upper() for k in kw2_set}

        for ln in range(start_ln, end_ln + 1):
            line = widget.get(f"{ln}.0", f"{ln}.end")

            # 1. Encontrar cadenas
            str_ranges = _find_string_ranges(line, cfg.string_delimiters)

            # 2. Encontrar inicio de comentario de línea
            cm_start = _find_comment_start(line, cfg.comment_line, str_ranges)

            # 3. Aplicar cadenas (solo antes del comentario)
            for s, e in str_ranges:
                if cm_start is None or s < cm_start:
                    widget.tag_add(tag_st, f"{ln}.{s}", f"{ln}.{e}")

            # 4. Aplicar comentario de línea
            if cm_start is not None:
                widget.tag_add(tag_cm, f"{ln}.{cm_start}", f"{ln}.end")

            # 5. Aplicar keywords en la zona sin strings ni comentarios
            effective_end = cm_start if cm_start is not None else len(line)
            effective_text = line[:effective_end]

            for m in re.finditer(r'\b[A-Za-z_][A-Za-z_0-9]*\b', effective_text):
                word = m.group()
                s, e = m.start(), m.end()
                if any(rs <= s < re_ for rs, re_ in str_ranges):
                    continue
                if case_sensitive:
                    if word in kw_set:
                        widget.tag_add(tag_kw, f"{ln}.{s}", f"{ln}.{e}")
                    elif kw2_set and word in kw2_set:
                        widget.tag_add(tag_kw2, f"{ln}.{s}", f"{ln}.{e}")
                else:
                    wu = word.upper()
                    if wu in kw_upper:
                        widget.tag_add(tag_kw, f"{ln}.{s}", f"{ln}.{e}")
                    elif kw2_upper and wu in kw2_upper:
                        widget.tag_add(tag_kw2, f"{ln}.{s}", f"{ln}.{e}")


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

    def __init__(self, colors: MdEditorColors, code_configs: dict | None = None):
        super().__init__()
        self._c = colors
        self._code_hl = _CodeHighlighter(code_configs or {})

    def update_colors(self, colors: MdEditorColors):
        self._c = colors

    def update_code_configs(self, configs: dict):
        self._code_hl.update_configs(configs)

    def configure_tags(self, widget: tk.Text):
        c = self._c
        # Prioridad (mayor = último creado): codeblock > inline_code > link > heading
        # > bold > italic > list_marker > quote > hr > strikethrough
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
        # Tags de código por lenguaje (mayor prioridad que md_codeblock)
        self._code_hl.configure_tags(widget)

    def highlight(self, widget: tk.Text):
        all_tags = (
            "md_strikethrough", "md_hr", "md_quote", "md_list_mark",
            "md_italic", "md_bold", "md_heading", "md_link",
            "md_code", "md_codeblock",
        )
        for tag in all_tags:
            widget.tag_remove(tag, "1.0", tk.END)
        self._code_hl.remove_tags_in_range(widget, "1.0", tk.END)

        content = widget.get("1.0", tk.END)
        lines = content.split("\n")
        in_code_block = False
        code_lang = ""
        code_start_ln = 0

        for i, line in enumerate(lines):
            ln = i + 1
            s = f"{ln}.0"
            e = f"{ln}.end"

            # ── Bloques de código (triple backtick) ──────────────────────
            if line.startswith("```"):
                if not in_code_block:
                    # Inicio del bloque
                    in_code_block = True
                    code_lang = line[3:].strip()
                    code_start_ln = ln
                    widget.tag_add("md_codeblock", s, e)
                else:
                    # Fin del bloque
                    widget.tag_add("md_codeblock", s, e)
                    in_code_block = False
                    # Resaltar contenido del bloque con colores del lenguaje
                    if code_lang and code_start_ln < ln - 1:
                        self._code_hl.highlight_block(
                            widget, code_start_ln + 1, ln - 1, code_lang,
                        )
                    code_lang = ""
                    code_start_ln = 0
                continue

            if in_code_block:
                widget.tag_add("md_codeblock", s, e)
                continue

            # ── Encabezados ───────────────────────────────────────────────
            if re.match(r"^#{1,6}\s", line):
                widget.tag_add("md_heading", s, e)
                continue

            # ── Cita ──────────────────────────────────────────────────────
            if line.startswith("> "):
                widget.tag_add("md_quote", s, e)
                continue

            # ── Línea horizontal ──────────────────────────────────────────
            if re.match(r"^(\s*[-*_]){3,}\s*$", line):
                widget.tag_add("md_hr", s, e)
                continue

            # ── Marcadores de lista ───────────────────────────────────────
            for m in re.finditer(r"^(\s*[*\-+]|\s*\d+\.)\s", line):
                widget.tag_add("md_list_mark", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # ── Tachado ~~...~~ ───────────────────────────────────────────
            for m in re.finditer(r"~~[^~\n]+~~", line):
                widget.tag_add("md_strikethrough", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # ── Negrita+cursiva ***...*** ─────────────────────────────────
            for m in re.finditer(r"\*{3}[^*\n]+\*{3}", line):
                widget.tag_add("md_bold",   f"{ln}.{m.start()}", f"{ln}.{m.end()}")
                widget.tag_add("md_italic", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # ── Negrita **...** ───────────────────────────────────────────
            for m in re.finditer(r"\*\*[^*\n]+\*\*|__[^_\n]+__", line):
                widget.tag_add("md_bold", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # ── Cursiva *...* ─────────────────────────────────────────────
            for m in re.finditer(r"(?<!\*)\*[^*\n]+\*(?!\*)|(?<!_)_[^_\n]+_(?!_)", line):
                widget.tag_add("md_italic", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # ── Código inline `...` ───────────────────────────────────────
            for m in re.finditer(r"`[^`\n]+`", line):
                widget.tag_add("md_code", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # ── Enlace/imagen [...](...)  ─────────────────────────────────
            for m in re.finditer(r"!?\[[^\]\n]*\]\([^\)\n]*\)", line):
                widget.tag_add("md_link", f"{ln}.{m.start()}", f"{ln}.{m.end()}")


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

class LatexHighlighter(_BaseHighlighter):

    def __init__(self, colors: LatexEditorColors, code_configs: dict | None = None):
        super().__init__()
        self._c = colors
        self._code_hl = _CodeHighlighter(code_configs or {})

    def update_colors(self, colors: LatexEditorColors):
        self._c = colors

    def update_code_configs(self, configs: dict):
        self._code_hl.update_configs(configs)

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
        # Tags de código por lenguaje (mayor prioridad que los de LaTeX)
        self._code_hl.configure_tags(widget)

    def highlight(self, widget: tk.Text):
        all_tags = ("ltx_bracket", "ltx_brace", "ltx_special",
                    "ltx_cmd", "ltx_math", "ltx_env", "ltx_comment")
        for tag in all_tags:
            widget.tag_remove(tag, "1.0", tk.END)
        self._code_hl.remove_tags_in_range(widget, "1.0", tk.END)

        content = widget.get("1.0", tk.END)
        lines = content.split("\n")

        # ── Detectar bloques lstlisting para resaltado de código ─────────
        # Formato: \begin{lstlisting}[language=X, style=Y]
        code_blocks: list[tuple[int, int, str]] = []  # (start_ln, end_ln, lang)
        in_listing = False
        listing_lang = ""
        listing_start = 0

        for i, line in enumerate(lines):
            ln = i + 1
            if not in_listing:
                m = re.match(r"\\begin\{lstlisting\}(?:\[([^\]]*)\])?", line)
                if m:
                    in_listing = True
                    listing_start = ln
                    opts = m.group(1) or ""
                    lang_m = re.search(r"\blanguage\s*=\s*([A-Za-z0-9_+#]+)", opts)
                    listing_lang = lang_m.group(1) if lang_m else ""
            else:
                if re.match(r"\\end\{lstlisting\}", line):
                    in_listing = False
                    if listing_lang and listing_start < ln - 1:
                        code_blocks.append((listing_start + 1, ln - 1, listing_lang))

        # ── Resaltado LaTeX línea a línea ─────────────────────────────────
        # Identificar líneas dentro de bloques lstlisting
        listing_lines: set[int] = set()
        for s_ln, e_ln, _ in code_blocks:
            for ln in range(s_ln, e_ln + 1):
                listing_lines.add(ln)

        for i, line in enumerate(lines):
            ln = i + 1

            # Las líneas de código no reciben resaltado LaTeX (solo código)
            if ln in listing_lines:
                continue

            comment_start = None
            m = re.search(r"(?<!\\)%", line)
            if m:
                comment_start = m.start()
                effective_line = line[:comment_start]
            else:
                effective_line = line

            # Entornos \begin{} y \end{}
            for m in re.finditer(r"\\(?:begin|end)\{[^}]*\}", effective_line):
                widget.tag_add("ltx_env", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Comandos \palabra
            for m in re.finditer(r"\\[a-zA-Z@]+\*?", effective_line):
                widget.tag_add("ltx_cmd", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Matemáticas $...$
            for m in re.finditer(r"\$[^$\n]*\$", effective_line):
                widget.tag_add("ltx_math", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Caracteres especiales & ^ _ ~
            for m in re.finditer(r"(?<!\\)[&^_~]", effective_line):
                widget.tag_add("ltx_special", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Llaves { }
            for m in re.finditer(r"(?<!\\)[{}]", effective_line):
                widget.tag_add("ltx_brace", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Corchetes [ ]
            for m in re.finditer(r"[\[\]]", effective_line):
                widget.tag_add("ltx_bracket", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

            # Comentario
            if comment_start is not None:
                widget.tag_add("ltx_comment", f"{ln}.{comment_start}", f"{ln}.end")

        # ── Aplicar resaltado de código en bloques lstlisting ─────────────
        for s_ln, e_ln, lang in code_blocks:
            self._code_hl.highlight_block(widget, s_ln, e_ln, lang)


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

            tag_range("html_bracket", base, base + 1)
            tag_range("html_bracket", base + len(tag_text) - 1, base + len(tag_text))

            name_m = re.match(r"</?([a-zA-Z][a-zA-Z0-9\-]*)", tag_text)
            if name_m:
                tag_range("html_tag_name",
                          base + name_m.start(1), base + name_m.end(1))

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
        before = content[:char_pos]
        line = before.count("\n") + 1
        col  = char_pos - before.rfind("\n") - 1
        return f"{line}.{col}"
