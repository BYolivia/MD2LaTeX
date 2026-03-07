"""Pestaña de configuración de colores por lenguaje para lstlisting."""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, simpledialog

from model.language_color_config import (
    ElementStyle,
    LanguageColorConfig,
    COLORS_FOLDER,
    FONT_SIZES,
)


def _contrast_fg(hex_color: str) -> str:
    """Devuelve '#000000' o '#ffffff' según la luminancia del color de fondo."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return "#000000" if lum > 140 else "#ffffff"


class _ColorRow:
    """Fila de edición de estilo: selector de color + checkboxes negrita/cursiva."""

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        style: ElementStyle,
        on_change,
        show_style_checks: bool = True,
        bg: str = "#2a2a3d",
    ):
        self._on_change = on_change
        self._color = style.color
        self._bold_var = tk.BooleanVar(value=style.bold)
        self._italic_var = tk.BooleanVar(value=style.italic)

        row = tk.Frame(parent, bg=bg)
        row.pack(fill=tk.X, pady=3, padx=8)

        tk.Label(
            row, text=label, width=20, anchor=tk.W,
            bg=bg, fg="#cdd6f4", font=("Helvetica", 9),
        ).pack(side=tk.LEFT)

        self._btn = tk.Button(
            row, text=self._color.upper(),
            command=self._pick_color,
            relief=tk.FLAT, padx=8, pady=2,
            cursor="hand2", font=("Courier New", 9),
        )
        self._btn.pack(side=tk.LEFT, padx=(0, 8))
        self._refresh_btn()

        if show_style_checks:
            tk.Checkbutton(
                row, text="Negrita",
                variable=self._bold_var,
                command=self._on_change,
                bg=bg, fg="#cdd6f4",
                selectcolor="#313244",
                activebackground=bg,
                font=("Helvetica", 9),
            ).pack(side=tk.LEFT, padx=4)

            tk.Checkbutton(
                row, text="Cursiva",
                variable=self._italic_var,
                command=self._on_change,
                bg=bg, fg="#cdd6f4",
                selectcolor="#313244",
                activebackground=bg,
                font=("Helvetica", 9),
            ).pack(side=tk.LEFT, padx=4)

    def _pick_color(self):
        result = colorchooser.askcolor(
            color=self._color,
            title="Seleccionar color",
        )
        if result and result[1]:
            self._color = result[1].upper()
            self._refresh_btn()
            self._on_change()

    def _refresh_btn(self):
        fg = _contrast_fg(self._color)
        self._btn.configure(bg=self._color, fg=fg, text=self._color.upper())

    def get(self) -> ElementStyle:
        return ElementStyle(
            color=self._color,
            bold=self._bold_var.get(),
            italic=self._italic_var.get(),
        )

    def set(self, style: ElementStyle):
        self._color = style.color
        self._bold_var.set(style.bold)
        self._italic_var.set(style.italic)
        self._refresh_btn()


class LanguageColorsTab:
    """Vista completa de la pestaña de configuración de colores."""

    BG = "#1e1e2e"
    BG_PANEL = "#2a2a3d"
    BG_LIST = "#1a1a2a"
    BG_PREVIEW = "#0d1a0d"
    FG = "#cdd6f4"
    FG_ACCENT = "#a6e3a1"
    FG_STATUS = "#a6adc8"
    BTN_BG = "#313244"
    BTN_FG = "#cdd6f4"
    BTN_ACTIVE = "#45475a"

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=self.BG)
        self._controller = None
        self._current_config: LanguageColorConfig | None = None
        self._dirty = False
        self._build_ui()

    def set_controller(self, controller):
        self._controller = controller
        self._reload_list()

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        self._build_toolbar()

        content = tk.Frame(self.frame, bg=self.BG)
        content.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        self._build_language_list(content)
        self._build_form(content)
        self._build_statusbar()

    def _build_toolbar(self):
        tb = tk.Frame(self.frame, bg="#2a2a3d", pady=5)
        tb.pack(fill=tk.X)

        self._btn(tb, "+ Nuevo",     self._new_language).pack(side=tk.LEFT, padx=6)
        self._btn(tb, "Guardar",     self._save_current, fg="#a6e3a1").pack(side=tk.LEFT, padx=3)
        self._btn(tb, "Recargar",    self._reload_list).pack(side=tk.LEFT, padx=3)
        self._btn(tb, "Eliminar",    self._delete_current, fg="#f38ba8").pack(side=tk.LEFT, padx=3)
        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        self._btn(tb, "Abrir carpeta", self._open_folder).pack(side=tk.LEFT, padx=3)

    def _build_language_list(self, parent: tk.Frame):
        frame = tk.Frame(parent, bg=self.BG_PANEL, width=180)
        frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 6))
        frame.pack_propagate(False)

        tk.Label(
            frame, text="Lenguajes configurados",
            bg=self.BG_PANEL, fg="#89dceb",
            font=("Helvetica", 10, "bold"), anchor=tk.W, padx=8, pady=4,
        ).pack(fill=tk.X)

        list_frame = tk.Frame(frame, bg=self.BG_LIST)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        self._listbox = tk.Listbox(
            list_frame,
            bg=self.BG_LIST, fg=self.FG,
            selectbackground="#45475a", selectforeground=self.FG,
            font=("Courier New", 10),
            relief=tk.FLAT, bd=0,
            activestyle="none",
        )
        self._listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vs = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self._listbox.yview)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        self._listbox.configure(yscrollcommand=vs.set)
        self._listbox.bind("<<ListboxSelect>>", self._on_language_selected)

    def _build_form(self, parent: tk.Frame):
        outer = tk.Frame(parent, bg=self.BG)
        outer.grid(row=0, column=1, sticky=tk.NSEW)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        # ── Encabezado del formulario ──
        hdr = tk.Frame(outer, bg=self.BG_PANEL)
        hdr.grid(row=0, column=0, sticky=tk.EW, pady=(0, 4))

        tk.Label(
            hdr, text="Lenguaje:",
            bg=self.BG_PANEL, fg=self.FG,
            font=("Helvetica", 10, "bold"), padx=8,
        ).pack(side=tk.LEFT)

        self._lang_var = tk.StringVar()
        self._lang_entry = tk.Entry(
            hdr, textvariable=self._lang_var,
            bg="#313244", fg=self.FG,
            insertbackground=self.FG,
            font=("Courier New", 11),
            relief=tk.FLAT, bd=4, width=20,
        )
        self._lang_entry.pack(side=tk.LEFT, padx=4)

        # ── Cuerpo del formulario en dos columnas ──
        body = tk.Frame(outer, bg=self.BG)
        body.grid(row=1, column=0, sticky=tk.NSEW)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # Columna izquierda: colores
        left = tk.LabelFrame(
            body, text=" Colores de elementos ",
            bg=self.BG_PANEL, fg="#89b4fa",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, bd=1,
        )
        left.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 4), pady=4)

        self._kw_row = _ColorRow(
            left, "Palabras clave:",
            ElementStyle("#0055CC", bold=True), self._on_change, bg=self.BG_PANEL,
        )
        self._cm_row = _ColorRow(
            left, "Comentarios:",
            ElementStyle("#558855", italic=True), self._on_change, bg=self.BG_PANEL,
        )
        self._st_row = _ColorRow(
            left, "Cadenas de texto:",
            ElementStyle("#CC3300"), self._on_change, bg=self.BG_PANEL,
        )

        # Identificadores (con checkbox de activación)
        id_frame = tk.Frame(left, bg=self.BG_PANEL)
        id_frame.pack(fill=tk.X, pady=(4, 0), padx=8)

        self._use_id_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            id_frame, text="Identificadores (color personalizado):",
            variable=self._use_id_var,
            command=self._on_change,
            bg=self.BG_PANEL, fg=self.FG,
            selectcolor="#313244", activebackground=self.BG_PANEL,
            font=("Helvetica", 9),
        ).pack(anchor=tk.W)

        self._id_row = _ColorRow(
            left, "",
            ElementStyle("#000000"), self._on_change,
            show_style_checks=True, bg=self.BG_PANEL,
        )

        # Columna derecha: opciones visuales
        right = tk.LabelFrame(
            body, text=" Opciones visuales ",
            bg=self.BG_PANEL, fg="#89b4fa",
            font=("Helvetica", 9, "bold"),
            relief=tk.FLAT, bd=1,
        )
        right.grid(row=0, column=1, sticky=tk.NSEW, padx=(4, 0), pady=4)

        # Fondo
        bg_frame = tk.Frame(right, bg=self.BG_PANEL)
        bg_frame.pack(fill=tk.X, pady=6, padx=8)

        self._use_bg_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            bg_frame, text="Color de fondo:",
            variable=self._use_bg_var,
            command=self._on_change,
            bg=self.BG_PANEL, fg=self.FG,
            selectcolor="#313244", activebackground=self.BG_PANEL,
            font=("Helvetica", 9),
        ).pack(side=tk.LEFT)

        self._bg_color = "#F8F8F8"
        self._bg_btn = tk.Button(
            bg_frame, text=self._bg_color,
            command=self._pick_bg_color,
            relief=tk.FLAT, padx=8, pady=2,
            cursor="hand2", font=("Courier New", 9),
        )
        self._bg_btn.pack(side=tk.LEFT, padx=6)
        self._refresh_bg_btn()

        # Tamaño de fuente
        sz_frame = tk.Frame(right, bg=self.BG_PANEL)
        sz_frame.pack(fill=tk.X, pady=6, padx=8)

        tk.Label(
            sz_frame, text="Tamaño de fuente:",
            bg=self.BG_PANEL, fg=self.FG, font=("Helvetica", 9),
        ).pack(side=tk.LEFT)

        self._font_size_var = tk.StringVar(value="small")
        ttk.Combobox(
            sz_frame,
            textvariable=self._font_size_var,
            values=FONT_SIZES,
            state="readonly",
            width=14,
            font=("Courier New", 9),
        ).pack(side=tk.LEFT, padx=6)
        self._font_size_var.trace_add("write", lambda *_: self._on_change())

        # ── Vista previa ──────────────────────────────────────────────────
        prev_frame = tk.LabelFrame(
            outer, text=" Vista previa del código LaTeX generado ",
            bg=self.BG_PREVIEW, fg=self.FG_ACCENT,
            font=("Helvetica", 9, "bold"), relief=tk.FLAT,
        )
        prev_frame.grid(row=2, column=0, sticky=tk.NSEW, pady=(4, 0))
        outer.rowconfigure(2, weight=0)

        self._preview_text = tk.Text(
            prev_frame,
            bg=self.BG_PREVIEW, fg=self.FG_ACCENT,
            font=("Courier New", 9),
            wrap=tk.NONE, relief=tk.FLAT,
            padx=8, pady=6, state=tk.DISABLED, height=8,
        )
        self._preview_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vs2 = ttk.Scrollbar(prev_frame, orient=tk.VERTICAL, command=self._preview_text.yview)
        vs2.pack(side=tk.RIGHT, fill=tk.Y)
        self._preview_text.configure(yscrollcommand=vs2.set)

        tk.Button(
            outer, text="Copiar código LaTeX",
            command=self._copy_preview,
            bg=self.BTN_BG, fg=self.FG_ACCENT,
            activebackground=self.BTN_ACTIVE, activeforeground=self.FG_ACCENT,
            relief=tk.FLAT, padx=10, pady=3,
            cursor="hand2", font=("Helvetica", 9),
        ).grid(row=3, column=0, sticky=tk.E, pady=(2, 0))

    def _build_statusbar(self):
        bar = tk.Frame(self.frame, bg="#2a2a3d", pady=3)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._status_var = tk.StringVar(value="Selecciona un lenguaje o crea uno nuevo.")
        tk.Label(
            bar, textvariable=self._status_var,
            bg="#2a2a3d", fg=self.FG_STATUS,
            font=("Helvetica", 9), anchor=tk.W, padx=10,
        ).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # Lógica de la lista de lenguajes
    # ------------------------------------------------------------------

    def _reload_list(self):
        if not self._controller:
            return
        self._configs = self._controller.get_color_configs()
        self._listbox.delete(0, tk.END)
        for lang in sorted(self._configs):
            self._listbox.insert(tk.END, f"  {lang}")
        self._status_var.set(f"{len(self._configs)} lenguaje(s) configurado(s).")

    def _on_language_selected(self, _event=None):
        sel = self._listbox.curselection()
        if not sel:
            return
        lang = self._listbox.get(sel[0]).strip()
        if lang in self._configs:
            self._load_config(self._configs[lang])

    def _load_config(self, cfg: LanguageColorConfig):
        self._current_config = cfg
        self._lang_var.set(cfg.language)
        self._kw_row.set(cfg.keywords)
        self._cm_row.set(cfg.comments)
        self._st_row.set(cfg.strings)
        self._id_row.set(cfg.identifiers)
        self._use_id_var.set(cfg.use_identifier_color)
        self._use_bg_var.set(cfg.use_background)
        self._bg_color = cfg.background_color
        self._refresh_bg_btn()
        self._font_size_var.set(cfg.font_size)
        self._dirty = False
        self._update_preview()
        self._status_var.set(f"Editando: {cfg.language}")

    def _build_config_from_form(self) -> LanguageColorConfig:
        return LanguageColorConfig(
            language=self._lang_var.get().strip(),
            keywords=self._kw_row.get(),
            comments=self._cm_row.get(),
            strings=self._st_row.get(),
            identifiers=self._id_row.get(),
            use_identifier_color=self._use_id_var.get(),
            use_background=self._use_bg_var.get(),
            background_color=self._bg_color,
            font_size=self._font_size_var.get(),
        )

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _new_language(self):
        name = simpledialog.askstring(
            "Nuevo lenguaje",
            "Nombre del lenguaje (ej: python, typescript, go):",
            parent=self.frame,
        )
        if not name or not name.strip():
            return
        name = name.strip().lower()
        if name in self._configs:
            if not messagebox.askyesno(
                "Ya existe",
                f"Ya hay configuración para '{name}'. ¿Sobreescribir?",
                parent=self.frame,
            ):
                return
        cfg = LanguageColorConfig(language=name)
        self._load_config(cfg)
        self._status_var.set(f"Nuevo lenguaje: {name}  (sin guardar)")

    def _save_current(self):
        cfg = self._build_config_from_form()
        if not cfg.language:
            messagebox.showwarning("Sin nombre", "Indica el nombre del lenguaje.", parent=self.frame)
            return
        if not self._controller:
            return
        path = self._controller.save_color_config(cfg)
        self._dirty = False
        self._reload_list()
        self._status_var.set(f"Guardado: {path}")
        # Seleccionar el lenguaje guardado en la lista
        for i in range(self._listbox.size()):
            if self._listbox.get(i).strip() == cfg.language.lower():
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(i)
                self._listbox.see(i)
                break

    def _delete_current(self):
        sel = self._listbox.curselection()
        if not sel:
            messagebox.showinfo("Sin selección", "Selecciona un lenguaje para eliminar.", parent=self.frame)
            return
        lang = self._listbox.get(sel[0]).strip()
        if not messagebox.askyesno(
            "Eliminar",
            f"¿Eliminar la configuración de '{lang}'?",
            parent=self.frame,
        ):
            return
        if self._controller:
            self._controller.delete_color_config(lang)
        self._reload_list()
        self._current_config = None
        self._status_var.set(f"'{lang}' eliminado.")

    def _open_folder(self):
        if not self._controller:
            return
        folder = self._controller.get_colors_folder()
        folder.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                import os
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.frame)

    # ------------------------------------------------------------------
    # Color de fondo
    # ------------------------------------------------------------------

    def _pick_bg_color(self):
        result = colorchooser.askcolor(color=self._bg_color, title="Color de fondo")
        if result and result[1]:
            self._bg_color = result[1].upper()
            self._refresh_bg_btn()
            self._on_change()

    def _refresh_bg_btn(self):
        fg = _contrast_fg(self._bg_color)
        self._bg_btn.configure(bg=self._bg_color, fg=fg, text=self._bg_color.upper())

    # ------------------------------------------------------------------
    # Preview
    # ------------------------------------------------------------------

    def _on_change(self):
        self._dirty = True
        self._update_preview()

    def _update_preview(self):
        try:
            cfg = self._build_config_from_form()
            code = cfg.to_latex() if cfg.language else "% Indica el nombre del lenguaje"
        except Exception as e:
            code = f"% Error: {e}"
        self._preview_text.configure(state=tk.NORMAL)
        self._preview_text.delete("1.0", tk.END)
        self._preview_text.insert("1.0", code)
        self._preview_text.configure(state=tk.DISABLED)

    def _copy_preview(self):
        content = self._preview_text.get("1.0", tk.END).strip()
        self.frame.winfo_toplevel().clipboard_clear()
        self.frame.winfo_toplevel().clipboard_append(content)
        self._status_var.set("Código LaTeX copiado al portapapeles.")

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _btn(self, parent, text, command, fg=None):
        return tk.Button(
            parent, text=text, command=command,
            bg=self.BTN_BG, fg=fg or self.BTN_FG,
            activebackground=self.BTN_ACTIVE, activeforeground=fg or self.BTN_FG,
            relief=tk.FLAT, padx=10, pady=4,
            cursor="hand2", font=("Helvetica", 9),
        )
