"""Formulario de configuración de colores para los editores (MD, LaTeX, HTML)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from model.editor_color_config import MdEditorColors, LatexEditorColors, HtmlEditorColors
from view.language_colors_tab import _ColorRow   # reutilizamos el widget de color


_BG = "#1e1e2e"
_BG_PANEL = "#2a2a3d"
_BG_PREVIEW = "#0d1a0d"
_FG = "#cdd6f4"
_FG_ACCENT = "#a6e3a1"
_FG_STATUS = "#a6adc8"
_BTN_BG = "#313244"
_BTN_FG = "#cdd6f4"
_BTN_ACTIVE = "#45475a"


def _btn(parent, text, cmd, fg=None):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=_BTN_BG, fg=fg or _BTN_FG,
        activebackground=_BTN_ACTIVE, activeforeground=fg or _BTN_FG,
        relief=tk.FLAT, padx=10, pady=4,
        cursor="hand2", font=("Helvetica", 9),
    )


class _CheckRow:
    """Fila simple con un checkbox."""
    def __init__(self, parent, label: str, value: bool, on_change, bg=_BG_PANEL):
        self._var = tk.BooleanVar(value=value)
        tk.Checkbutton(
            parent, text=label,
            variable=self._var, command=on_change,
            bg=bg, fg=_FG, selectcolor="#313244",
            activebackground=bg, font=("Helvetica", 9),
        ).pack(anchor=tk.W, padx=8, pady=2)

    def get(self) -> bool:
        return self._var.get()

    def set(self, value: bool):
        self._var.set(value)


def _section(parent, title: str) -> tk.Frame:
    """Crea un LabelFrame de sección con estilo."""
    f = tk.LabelFrame(
        parent, text=f" {title} ",
        bg=_BG_PANEL, fg="#89b4fa",
        font=("Helvetica", 9, "bold"),
        relief=tk.FLAT, bd=1,
    )
    f.pack(fill=tk.X, padx=8, pady=4)
    return f


# ---------------------------------------------------------------------------
# Sub-formularios por tipo de editor
# ---------------------------------------------------------------------------

class _MdColorsForm:
    def __init__(self, parent: tk.Widget, colors: MdEditorColors, on_change):
        self._oc = on_change
        frame = tk.Frame(parent, bg=_BG_PANEL)
        frame.pack(fill=tk.BOTH, expand=True)

        s1 = _section(frame, "Estructura")
        self._heading    = _ColorRow(s1, "Encabezados (#):",   colors._col("heading"),    on_change, bg=_BG_PANEL)
        self._heading_b  = _CheckRow(s1, "Encabezados en negrita", colors.heading_bold, on_change, bg=_BG_PANEL)
        self._quote      = _ColorRow(s1, "Citas (>):",          colors._col("quote"),     on_change, show_style_checks=False, bg=_BG_PANEL)
        self._quote_i    = _CheckRow(s1, "Citas en cursiva",    colors.quote_italic,      on_change, bg=_BG_PANEL)
        self._hr         = _ColorRow(s1, "Línea horizontal:",   colors._col("hr_color"),  on_change, show_style_checks=False, bg=_BG_PANEL)
        self._list_mark  = _ColorRow(s1, "Marcadores de lista:",colors._col("list_marker"),on_change, show_style_checks=False, bg=_BG_PANEL)

        s2 = _section(frame, "Énfasis inline")
        self._bold       = _ColorRow(s2, "Negrita (**):",       colors._col("bold_text"), on_change, show_style_checks=False, bg=_BG_PANEL)
        self._italic     = _ColorRow(s2, "Cursiva (*):",        colors._col("italic_text"),on_change, show_style_checks=False, bg=_BG_PANEL)
        self._strike     = _ColorRow(s2, "Tachado (~~):",       colors._col("strikethrough"),on_change, show_style_checks=False, bg=_BG_PANEL)
        self._link       = _ColorRow(s2, "Enlace/Imagen:",      colors._col("link"),      on_change, show_style_checks=False, bg=_BG_PANEL)

        s3 = _section(frame, "Código")
        self._code       = _ColorRow(s3, "Código inline (`):",  colors._col("inline_code"),on_change, show_style_checks=False, bg=_BG_PANEL)
        self._code_bg    = _ColorRow(s3, "Fondo código inline:",colors._col("inline_code_bg"),on_change, show_style_checks=False, bg=_BG_PANEL)
        self._codeblock  = _ColorRow(s3, "Bloque de código:",   colors._col("code_block"),on_change, show_style_checks=False, bg=_BG_PANEL)
        self._codeblock_bg = _ColorRow(s3, "Fondo bloque código:",colors._col("code_block_bg"),on_change, show_style_checks=False, bg=_BG_PANEL)

    def build(self) -> MdEditorColors:
        return MdEditorColors(
            heading=self._heading.get().color,
            heading_bold=self._heading_b.get(),
            bold_text=self._bold.get().color,
            italic_text=self._italic.get().color,
            inline_code=self._code.get().color,
            inline_code_bg=self._code_bg.get().color,
            code_block=self._codeblock.get().color,
            code_block_bg=self._codeblock_bg.get().color,
            link=self._link.get().color,
            quote=self._quote.get().color,
            quote_italic=self._quote_i.get(),
            hr_color=self._hr.get().color,
            list_marker=self._list_mark.get().color,
            strikethrough=self._strike.get().color,
        )


class _LatexColorsForm:
    def __init__(self, parent: tk.Widget, colors: LatexEditorColors, on_change):
        frame = tk.Frame(parent, bg=_BG_PANEL)
        frame.pack(fill=tk.BOTH, expand=True)

        s1 = _section(frame, "Comandos y entornos")
        self._cmd      = _ColorRow(s1, r"Comandos (\cmd):",    colors._col("command"),     on_change, bg=_BG_PANEL)
        self._cmd_b    = _CheckRow(s1, "Comandos en negrita",  colors.command_bold,         on_change, bg=_BG_PANEL)
        self._env      = _ColorRow(s1, r"Entornos (\begin{}):",colors._col("environment"),  on_change, show_style_checks=False, bg=_BG_PANEL)
        self._env_b    = _CheckRow(s1, "Entornos en negrita",  colors.environment_bold,     on_change, bg=_BG_PANEL)

        s2 = _section(frame, "Elementos inline")
        self._math     = _ColorRow(s2, "Matemáticas ($):",     colors._col("math"),         on_change, show_style_checks=False, bg=_BG_PANEL)
        self._special  = _ColorRow(s2, "Especiales (& ^ _):",  colors._col("special"),      on_change, show_style_checks=False, bg=_BG_PANEL)
        self._brace    = _ColorRow(s2, "Llaves { }:",          colors._col("braces"),       on_change, show_style_checks=False, bg=_BG_PANEL)
        self._bracket  = _ColorRow(s2, "Corchetes [ ]:",       colors._col("brackets"),     on_change, show_style_checks=False, bg=_BG_PANEL)

        s3 = _section(frame, "Comentarios")
        self._comment  = _ColorRow(s3, "Comentarios (%):",     colors._col("comment"),      on_change, show_style_checks=False, bg=_BG_PANEL)
        self._comment_i = _CheckRow(s3, "Comentarios en cursiva", colors.comment_italic,    on_change, bg=_BG_PANEL)

    def build(self) -> LatexEditorColors:
        return LatexEditorColors(
            command=self._cmd.get().color,
            command_bold=self._cmd_b.get(),
            environment=self._env.get().color,
            environment_bold=self._env_b.get(),
            math=self._math.get().color,
            comment=self._comment.get().color,
            comment_italic=self._comment_i.get(),
            braces=self._brace.get().color,
            brackets=self._bracket.get().color,
            special=self._special.get().color,
        )


class _HtmlColorsForm:
    def __init__(self, parent: tk.Widget, colors: HtmlEditorColors, on_change):
        frame = tk.Frame(parent, bg=_BG_PANEL)
        frame.pack(fill=tk.BOTH, expand=True)

        s1 = _section(frame, "Etiquetas")
        self._tag_name    = _ColorRow(s1, "Nombre de etiqueta:", colors._col("tag_name"),    on_change, show_style_checks=False, bg=_BG_PANEL)
        self._bracket     = _ColorRow(s1, "Ángulos < >:",         colors._col("tag_bracket"), on_change, show_style_checks=False, bg=_BG_PANEL)
        self._doctype     = _ColorRow(s1, "DOCTYPE:",             colors._col("doctype"),     on_change, show_style_checks=False, bg=_BG_PANEL)

        s2 = _section(frame, "Atributos y valores")
        self._attr        = _ColorRow(s2, "Atributos:",           colors._col("attribute"),   on_change, show_style_checks=False, bg=_BG_PANEL)
        self._value       = _ColorRow(s2, "Valores (\"..\"):",    colors._col("value"),       on_change, show_style_checks=False, bg=_BG_PANEL)
        self._entity      = _ColorRow(s2, "Entidades (&amp;):",   colors._col("entity"),      on_change, show_style_checks=False, bg=_BG_PANEL)

        s3 = _section(frame, "Comentarios y scripts")
        self._comment     = _ColorRow(s3, "Comentarios:",         colors._col("comment"),     on_change, show_style_checks=False, bg=_BG_PANEL)
        self._comment_i   = _CheckRow(s3, "Comentarios en cursiva", colors.comment_italic,   on_change, bg=_BG_PANEL)
        self._script      = _ColorRow(s3, "Script/Style:",        colors._col("script_style"),on_change, show_style_checks=False, bg=_BG_PANEL)

    def build(self) -> HtmlEditorColors:
        return HtmlEditorColors(
            tag_name=self._tag_name.get().color,
            tag_bracket=self._bracket.get().color,
            attribute=self._attr.get().color,
            value=self._value.get().color,
            comment=self._comment.get().color,
            comment_italic=self._comment_i.get(),
            doctype=self._doctype.get().color,
            entity=self._entity.get().color,
            script_style=self._script.get().color,
        )


# ---------------------------------------------------------------------------
# Vista principal del formulario de colores de editor
# ---------------------------------------------------------------------------

class EditorColorsForm:
    """
    Pestaña con sub-pestañas para configurar los colores de los
    editores MD, LaTeX y HTML.
    """

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=_BG)
        self._on_save_callbacks: list = []
        self._build_ui()

    def add_on_save(self, callback):
        """Registra una función que se llamará cuando se guarden los colores."""
        self._on_save_callbacks.append(callback)

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build_ui(self):
        from model.editor_color_config import MdEditorColors, LatexEditorColors, HtmlEditorColors
        self._md_colors    = MdEditorColors.load()
        self._latex_colors = LatexEditorColors.load()
        self._html_colors  = HtmlEditorColors.load()

        # Toolbar
        tb = tk.Frame(self.frame, bg=_BG_PANEL, pady=5)
        tb.pack(fill=tk.X)
        _btn(tb, "Guardar todos", self._save_all, fg=_FG_ACCENT).pack(side=tk.LEFT, padx=8)
        _btn(tb, "Restaurar por defecto", self._restore_defaults, fg="#f38ba8").pack(side=tk.LEFT, padx=4)

        # Sub-notebook
        style = ttk.Style()
        style.configure("Inner.TNotebook", background=_BG, borderwidth=0)
        style.configure("Inner.TNotebook.Tab", background="#2a2a3d", foreground=_FG_STATUS,
                        padding=[10, 4], font=("Helvetica", 9))
        style.map("Inner.TNotebook.Tab",
                  background=[("selected", _BG)],
                  foreground=[("selected", _FG)])

        nb = ttk.Notebook(self.frame, style="Inner.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # ── MD ──────────────────────────────────────────────────────────
        md_outer = tk.Frame(nb, bg=_BG)
        nb.add(md_outer, text="  Editor MD  ")
        md_canvas, md_inner = self._scrollable(md_outer)
        self._md_form = _MdColorsForm(md_inner, self._md_colors, self._on_change)

        # ── LaTeX ────────────────────────────────────────────────────────
        ltx_outer = tk.Frame(nb, bg=_BG)
        nb.add(ltx_outer, text="  Editor LaTeX  ")
        ltx_canvas, ltx_inner = self._scrollable(ltx_outer)
        self._ltx_form = _LatexColorsForm(ltx_inner, self._latex_colors, self._on_change)

        # ── HTML ─────────────────────────────────────────────────────────
        html_outer = tk.Frame(nb, bg=_BG)
        nb.add(html_outer, text="  Editor HTML  ")
        html_canvas, html_inner = self._scrollable(html_outer)
        self._html_form = _HtmlColorsForm(html_inner, self._html_colors, self._on_change)

        # Status bar
        bar = tk.Frame(self.frame, bg=_BG_PANEL, pady=3)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._status = tk.StringVar(value="Configura los colores y pulsa 'Guardar todos'.")
        tk.Label(bar, textvariable=self._status, bg=_BG_PANEL, fg=_FG_STATUS,
                 font=("Helvetica", 9), anchor=tk.W, padx=10).pack(fill=tk.X)

    def _scrollable(self, parent: tk.Frame):
        """Crea un frame con scroll vertical. Devuelve (canvas, inner_frame)."""
        canvas = tk.Canvas(parent, bg=_BG_PANEL, highlightthickness=0)
        vs = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vs.set)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=_BG_PANEL)
        win = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _on_configure(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(e):
            canvas.itemconfig(win, width=e.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        inner.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        return canvas, inner

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_change(self):
        self._status.set("Cambios sin guardar — pulsa 'Guardar todos' para aplicar.")

    def _save_all(self):
        self._md_colors    = self._md_form.build()
        self._latex_colors = self._ltx_form.build()
        self._html_colors  = self._html_form.build()
        self._md_colors.save()
        self._latex_colors.save()
        self._html_colors.save()
        self._status.set("Colores guardados. Los cambios se aplicarán al reiniciar la app.")
        for cb in self._on_save_callbacks:
            try:
                cb(self._md_colors, self._latex_colors, self._html_colors)
            except Exception:
                pass

    def _restore_defaults(self):
        from model.editor_color_config import MdEditorColors, LatexEditorColors, HtmlEditorColors
        defaults = (MdEditorColors(), LatexEditorColors(), HtmlEditorColors())
        for cfg in defaults:
            cfg.save()
        self._status.set("Colores restaurados a los valores por defecto. Reinicia para aplicarlos.")


# ---------------------------------------------------------------------------
# Parche: añadir método _col a los dataclasses para que _ColorRow funcione
# ---------------------------------------------------------------------------

from model.language_color_config import ElementStyle


def _col_helper(self, field_name: str) -> ElementStyle:
    """Devuelve un ElementStyle con solo el color del campo pedido."""
    return ElementStyle(color=getattr(self, field_name))


MdEditorColors._col    = _col_helper
LatexEditorColors._col = _col_helper
HtmlEditorColors._col  = _col_helper
