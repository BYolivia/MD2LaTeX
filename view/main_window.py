"""Vista principal de la aplicación (tkinter)."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from view.md_editor import MdEditorView
from view.language_colors_tab import LanguageColorsTab


class MainWindow:
    """Ventana principal con tres pestañas: Conversor, Editor MD y MD→HTML."""

    FONT_MONO = ("Courier New", 11)
    FONT_LABEL = ("Helvetica", 11, "bold")
    BG_MAIN = "#1e1e2e"
    BG_PANEL = "#2a2a3d"
    BG_TEXT = "#1a1a2a"
    FG_TEXT = "#cdd6f4"
    FG_LABEL_MD = "#89dceb"
    FG_LABEL_LATEX = "#f38ba8"
    FG_LABEL_HTML = "#a6e3a1"
    FG_STATUS = "#a6adc8"
    BTN_BG = "#313244"
    BTN_FG = "#cdd6f4"
    BTN_ACTIVE = "#45475a"
    ACCENT_MD = "#89b4fa"
    ACCENT_LATEX = "#fab387"
    ACCENT_HTML = "#a6e3a1"

    def __init__(self, root: tk.Tk):
        self.root = root
        self._controller = None
        self._build_ui()

    def set_controller(self, controller):
        self._controller = controller

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        self.root.title("MD \u2194 LaTeX / HTML Converter")
        self.root.geometry("1280x740")
        self.root.minsize(800, 500)
        self.root.configure(bg=self.BG_MAIN)
        self._build_notebook()

    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "App.TNotebook",
            background=self.BG_MAIN,
            borderwidth=0,
            tabmargins=[4, 4, 0, 0],
        )
        style.configure(
            "App.TNotebook.Tab",
            background=self.BG_PANEL,
            foreground=self.FG_STATUS,
            padding=[14, 6],
            font=("Helvetica", 10),
        )
        style.map(
            "App.TNotebook.Tab",
            background=[("selected", self.BG_MAIN)],
            foreground=[("selected", self.FG_TEXT)],
        )

        self._notebook = ttk.Notebook(self.root, style="App.TNotebook")
        self._notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña 1: Conversor MD ↔ LaTeX
        conv_frame = tk.Frame(self._notebook, bg=self.BG_MAIN)
        self._notebook.add(conv_frame, text="  MD \u2194 LaTeX  ")
        self._build_converter_tab(conv_frame)

        # Pestaña 2: Editor MD con preview
        self.md_editor = MdEditorView(self._notebook)
        self._notebook.add(self.md_editor.frame, text="  Editor MD  ")

        # Pestaña 3: MD → HTML
        html_frame = tk.Frame(self._notebook, bg=self.BG_MAIN)
        self._notebook.add(html_frame, text="  MD \u2192 HTML  ")
        self._build_html_tab(html_frame)

        # Pestaña 4: Colores de lenguajes
        self.lang_colors_tab = LanguageColorsTab(self._notebook)
        self._notebook.add(self.lang_colors_tab.frame, text="  Colores  ")

    # ------------------------------------------------------------------
    # Pestaña conversor MD ↔ LaTeX
    # ------------------------------------------------------------------

    def _build_converter_tab(self, parent: tk.Frame):
        self._build_toolbar(parent)
        self._build_main_area(parent)
        self._build_preamble_panel(parent)
        self._build_statusbar(parent)

    def _build_toolbar(self, parent: tk.Frame):
        toolbar = tk.Frame(parent, bg=self.BG_PANEL, pady=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        left = tk.Frame(toolbar, bg=self.BG_PANEL)
        left.pack(side=tk.LEFT, padx=8)

        self._btn(left, "Abrir MD", self._open_md).pack(side=tk.LEFT, padx=3)
        self._btn(left, "Abrir LaTeX", self._open_latex).pack(side=tk.LEFT, padx=3)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        self._btn(left, "Guardar MD", self._save_md).pack(side=tk.LEFT, padx=3)
        self._btn(left, "Guardar LaTeX", self._save_latex).pack(side=tk.LEFT, padx=3)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        center = tk.Frame(toolbar, bg=self.BG_PANEL)
        center.pack(side=tk.LEFT, padx=8)

        self._btn(
            center, "MD \u2192 LaTeX", self._on_md_to_latex,
            bg="#1e3a5f", fg=self.ACCENT_MD,
        ).pack(side=tk.LEFT, padx=3)
        self._btn(
            center, "LaTeX \u2192 MD", self._on_latex_to_md,
            bg="#3d1e1e", fg=self.ACCENT_LATEX,
        ).pack(side=tk.LEFT, padx=3)

        right = tk.Frame(toolbar, bg=self.BG_PANEL)
        right.pack(side=tk.RIGHT, padx=8)

        self._btn(right, "Limpiar todo", self._clear_all).pack(side=tk.RIGHT, padx=3)
        self._btn(right, "Copiar MD", self._copy_md).pack(side=tk.RIGHT, padx=3)
        self._btn(right, "Copiar LaTeX", self._copy_latex).pack(side=tk.RIGHT, padx=3)

    def _build_main_area(self, parent: tk.Frame):
        paned = tk.PanedWindow(
            parent, orient=tk.HORIZONTAL, bg=self.BG_MAIN,
            sashwidth=6, sashrelief=tk.FLAT,
        )
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        md_panel = _Panel(paned, "Markdown", self.FG_LABEL_MD, self)
        self._md_text = md_panel
        paned.add(md_panel.frame, minsize=300)

        latex_panel = _Panel(paned, "LaTeX", self.FG_LABEL_LATEX, self)
        self._latex_text = latex_panel
        paned.add(latex_panel.frame, minsize=300)

    def _build_preamble_panel(self, parent: tk.Frame):
        """Panel colapsable con dos secciones: importaciones y configuración."""
        self._preamble_visible = False
        _BG = "#111a11"
        _FG = "#a6e3a1"
        _BG2 = "#1a2a1a"

        container = tk.Frame(parent, bg=self.BG_MAIN)
        container.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0, 2))

        # ── Cabecera toggle ──────────────────────────────────────────────
        header = tk.Frame(container, bg=_BG2, pady=3)
        header.pack(fill=tk.X)

        self._preamble_toggle_var = tk.StringVar(value="▶  Preámbulo LaTeX necesario")
        tk.Button(
            header,
            textvariable=self._preamble_toggle_var,
            command=self._toggle_preamble,
            bg=_BG2, fg=_FG,
            activebackground="#253525", activeforeground=_FG,
            relief=tk.FLAT, anchor=tk.W, padx=8,
            font=("Helvetica", 9, "bold"), cursor="hand2",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._copy_all_btn = tk.Button(
            header, text="Copiar todo",
            command=self._copy_preamble_all,
            bg="#253525", fg=_FG,
            activebackground="#2e4a2e", activeforeground=_FG,
            relief=tk.FLAT, padx=8, pady=2,
            font=("Helvetica", 9), cursor="hand2",
        )

        # ── Contenido (oculto por defecto) ──────────────────────────────
        self._preamble_frame = tk.Frame(container, bg=_BG)

        # Sección 1: Importaciones
        self._preamble_frame.columnconfigure(0, weight=1)
        self._preamble_frame.columnconfigure(1, weight=1)
        self._preamble_frame.rowconfigure(1, weight=1)

        self._preamble_imports_text, copy_imp = self._preamble_section(
            self._preamble_frame, "Importaciones  (\\usepackage)", 0, _BG, _FG,
            copy_cmd=lambda: self._copy_section(self._preamble_imports_text),
        )
        self._preamble_config_text, copy_cfg = self._preamble_section(
            self._preamble_frame, "Configuración  (\\lstset, \\lstdefinelanguage, \\lstdefinestyle)", 1, _BG, _FG,
            copy_cmd=lambda: self._copy_section(self._preamble_config_text),
        )

    def _preamble_section(self, parent, title: str, col: int, bg: str, fg: str, copy_cmd):
        """Construye una subsección del panel de preámbulo. Devuelve (Text, copy_btn)."""
        frame = tk.Frame(parent, bg=bg)
        frame.grid(row=0, column=col, sticky=tk.NSEW, padx=(0 if col else 0, 4), pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        hdr = tk.Frame(frame, bg="#1a2a1a")
        hdr.grid(row=0, column=0, columnspan=2, sticky=tk.EW)
        tk.Label(hdr, text=title, bg="#1a2a1a", fg=fg,
                 font=("Helvetica", 8, "bold"), anchor=tk.W, padx=6, pady=2).pack(side=tk.LEFT)
        copy_btn = tk.Button(
            hdr, text="Copiar",
            command=copy_cmd,
            bg="#253525", fg=fg,
            activebackground="#2e4a2e", activeforeground=fg,
            relief=tk.FLAT, padx=6, pady=1,
            font=("Helvetica", 8), cursor="hand2",
        )
        copy_btn.pack(side=tk.RIGHT, padx=2)

        txt = tk.Text(
            frame, bg="#0d1a0d", fg=fg,
            insertbackground=fg,
            font=("Courier New", 9),
            wrap=tk.NONE, relief=tk.FLAT,
            padx=6, pady=4, state=tk.DISABLED, height=7,
        )
        txt.grid(row=1, column=0, sticky=tk.NSEW)
        vs = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=txt.yview)
        vs.grid(row=1, column=1, sticky=tk.NS)
        txt.configure(yscrollcommand=vs.set)
        txt.bind("<Control-a>", lambda e: self._select_all(txt))
        txt.bind("<Control-A>", lambda e: self._select_all(txt))
        return txt, copy_btn

    def _toggle_preamble(self):
        self._preamble_visible = not self._preamble_visible
        if self._preamble_visible:
            self._preamble_toggle_var.set("▼  Preámbulo LaTeX necesario")
            self._preamble_frame.pack(fill=tk.BOTH, ipady=2)
            self._copy_all_btn.pack(side=tk.RIGHT, padx=4)
        else:
            self._preamble_toggle_var.set("▶  Preámbulo LaTeX necesario")
            self._preamble_frame.pack_forget()
            self._copy_all_btn.pack_forget()

    def _copy_section(self, text_widget: tk.Text):
        content = text_widget.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.set_status("Copiado al portapapeles.")

    def _copy_preamble_all(self):
        imp = self._preamble_imports_text.get("1.0", tk.END).strip()
        cfg = self._preamble_config_text.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(f"{imp}\n\n{cfg}" if cfg else imp)
        self.set_status("Preámbulo completo copiado al portapapeles.")

    def _set_readonly_text(self, widget: tk.Text, content: str):
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.configure(state=tk.DISABLED)

    def set_preamble(self, imports: str, config: str):
        """Actualiza las dos secciones del panel de preámbulo."""
        self._set_readonly_text(self._preamble_imports_text, imports)
        self._set_readonly_text(self._preamble_config_text, config)
        has_content = bool(imports or config)
        if has_content and not self._preamble_visible:
            self._toggle_preamble()
        if not has_content and self._preamble_visible:
            self._toggle_preamble()

    def _build_statusbar(self, parent: tk.Frame):
        bar = tk.Frame(parent, bg=self.BG_PANEL, pady=3)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._status_var = tk.StringVar(value="Listo.")
        tk.Label(
            bar, textvariable=self._status_var,
            bg=self.BG_PANEL, fg=self.FG_STATUS,
            font=("Helvetica", 9), anchor=tk.W, padx=10,
        ).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # Pestaña MD → HTML
    # ------------------------------------------------------------------

    def _build_html_tab(self, parent: tk.Frame):
        # Toolbar
        toolbar = tk.Frame(parent, bg=self.BG_PANEL, pady=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        left = tk.Frame(toolbar, bg=self.BG_PANEL)
        left.pack(side=tk.LEFT, padx=8)

        self._btn(left, "Abrir MD", lambda: self._html_open_md()).pack(side=tk.LEFT, padx=3)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        self._btn(left, "Guardar HTML", lambda: self._html_save()).pack(side=tk.LEFT, padx=3)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        self._btn(
            left, "MD \u2192 HTML", self._on_md_to_html,
            bg="#1e3d22", fg=self.ACCENT_HTML,
        ).pack(side=tk.LEFT, padx=3)

        right = tk.Frame(toolbar, bg=self.BG_PANEL)
        right.pack(side=tk.RIGHT, padx=8)
        self._btn(right, "Copiar HTML", self._copy_html).pack(side=tk.RIGHT, padx=3)
        self._btn(right, "Limpiar", self._html_clear).pack(side=tk.RIGHT, padx=3)

        # Paneles
        paned = tk.PanedWindow(
            parent, orient=tk.HORIZONTAL, bg=self.BG_MAIN,
            sashwidth=6, sashrelief=tk.FLAT,
        )
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        md_panel = _Panel(paned, "Markdown", self.FG_LABEL_MD, self)
        self._html_md_text = md_panel
        paned.add(md_panel.frame, minsize=300)

        html_panel = _Panel(paned, "HTML generado", self.FG_LABEL_HTML, self)
        self._html_out_text = html_panel
        paned.add(html_panel.frame, minsize=300)

        # Statusbar
        bar = tk.Frame(parent, bg=self.BG_PANEL, pady=3)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._html_status_var = tk.StringVar(value="Listo.")
        tk.Label(
            bar, textvariable=self._html_status_var,
            bg=self.BG_PANEL, fg=self.FG_STATUS,
            font=("Helvetica", 9), anchor=tk.W, padx=10,
        ).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # API pública para el controlador (conversor MD ↔ LaTeX)
    # ------------------------------------------------------------------

    def get_md_text(self) -> str:
        return self._md_text.get_text()

    def get_latex_text(self) -> str:
        return self._latex_text.get_text()

    def set_md_text(self, text: str):
        self._md_text.set_text(text)

    def set_latex_text(self, text: str):
        self._latex_text.set_text(text)

    def set_status(self, message: str):
        self._status_var.set(message)

    def show_error(self, title: str, message: str):
        messagebox.showerror(title, message)

    def ask_open_file(self, filetypes) -> str:
        return filedialog.askopenfilename(filetypes=filetypes)

    def ask_save_file(self, filetypes, defaultextension) -> str:
        return filedialog.asksaveasfilename(
            filetypes=filetypes, defaultextension=defaultextension,
        )

    # API pública para el controlador (MD → HTML)

    def get_html_md_text(self) -> str:
        return self._html_md_text.get_text()

    def set_html_out_text(self, text: str):
        self._html_out_text.set_text(text)

    def set_html_status(self, message: str):
        self._html_status_var.set(message)

    # ------------------------------------------------------------------
    # Callbacks MD ↔ LaTeX
    # ------------------------------------------------------------------

    def _on_md_to_latex(self):
        if self._controller:
            self._controller.convert_md_to_latex()

    def _on_latex_to_md(self):
        if self._controller:
            self._controller.convert_latex_to_md()

    def _open_md(self):
        if self._controller:
            self._controller.open_file("md")

    def _open_latex(self):
        if self._controller:
            self._controller.open_file("latex")

    def _save_md(self):
        if self._controller:
            self._controller.save_file("md")

    def _save_latex(self):
        if self._controller:
            self._controller.save_file("latex")

    def _copy_md(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.get_md_text())
        self.set_status("Markdown copiado al portapapeles.")

    def _copy_latex(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.get_latex_text())
        self.set_status("LaTeX copiado al portapapeles.")

    def _clear_all(self):
        self.set_md_text("")
        self.set_latex_text("")
        self.set_status("Paneles limpiados.")

    # ------------------------------------------------------------------
    # Callbacks MD → HTML
    # ------------------------------------------------------------------

    def _on_md_to_html(self):
        if self._controller:
            self._controller.convert_md_to_html()

    def _html_open_md(self):
        if self._controller:
            self._controller.open_html_md_file()

    def _html_save(self):
        if self._controller:
            self._controller.save_html_file()

    def _copy_html(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self._html_out_text.get_text())
        self.set_html_status("HTML copiado al portapapeles.")

    def _html_clear(self):
        self._html_md_text.set_text("")
        self._html_out_text.set_text("")
        self.set_html_status("Paneles limpiados.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _select_all(widget: tk.Text) -> str:
        """Selecciona todo el texto de un widget Text. Devuelve 'break' para
        evitar que tkinter propague el evento con su comportamiento por defecto."""
        widget.tag_add(tk.SEL, "1.0", tk.END)
        widget.mark_set(tk.INSERT, "1.0")
        widget.see(tk.INSERT)
        return "break"

    def _btn(self, parent, text, command, bg=None, fg=None):
        return tk.Button(
            parent, text=text, command=command,
            bg=bg or self.BTN_BG, fg=fg or self.BTN_FG,
            activebackground=self.BTN_ACTIVE, activeforeground=self.BTN_FG,
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            font=("Helvetica", 9),
        )


class _Panel:
    """Panel reutilizable con etiqueta, área de texto y scrollbars."""

    def __init__(self, parent, label: str, fg_label: str, window: MainWindow):
        self.frame = tk.Frame(parent, bg=window.BG_PANEL)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        header = tk.Frame(self.frame, bg=window.BG_PANEL)
        header.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(4, 2))

        tk.Label(
            header, text=label,
            bg=window.BG_PANEL, fg=fg_label, font=window.FONT_LABEL,
        ).pack(side=tk.LEFT)

        self._info_var = tk.StringVar(value="0 líneas | 0 chars")
        tk.Label(
            header, textvariable=self._info_var,
            bg=window.BG_PANEL, fg=window.FG_STATUS, font=("Helvetica", 8),
        ).pack(side=tk.RIGHT)

        self._text = tk.Text(
            self.frame,
            bg=window.BG_TEXT, fg=window.FG_TEXT,
            insertbackground=window.FG_TEXT,
            selectbackground="#45475a",
            font=window.FONT_MONO, wrap=tk.NONE,
            undo=True, relief=tk.FLAT, padx=6, pady=6,
        )
        self._text.grid(row=1, column=0, sticky=tk.NSEW, padx=(4, 0), pady=(0, 4))

        vscroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self._text.yview)
        vscroll.grid(row=1, column=1, sticky=tk.NS, pady=(0, 4))
        hscroll = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self._text.xview)
        hscroll.grid(row=2, column=0, sticky=tk.EW, padx=(4, 0))

        self._text.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        self._text.bind("<<Modified>>", self._on_modified)
        self._text.bind("<Control-a>", lambda e: MainWindow._select_all(self._text))
        self._text.bind("<Control-A>", lambda e: MainWindow._select_all(self._text))

    def get_text(self) -> str:
        return self._text.get("1.0", tk.END).rstrip("\n")

    def set_text(self, text: str):
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", text)
        self._text.edit_modified(False)
        self._update_info()

    def _on_modified(self, _event=None):
        if self._text.edit_modified():
            self._update_info()
            self._text.edit_modified(False)

    def _update_info(self):
        content = self._text.get("1.0", tk.END)
        lines = content.count("\n")
        chars = len(content) - 1
        self._info_var.set(f"{lines} líneas | {chars} chars")
