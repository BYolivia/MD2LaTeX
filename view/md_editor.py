"""Vista del editor Markdown con previsualización en vivo."""

import tkinter as tk
from tkinter import ttk, filedialog
from tkinterweb import HtmlFrame

# CSS inyectado en el preview para aspecto limpio
_PREVIEW_CSS = """
<style>
  * { box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 15px;
    line-height: 1.7;
    color: #cdd6f4;
    background-color: #1a1a2a;
    padding: 24px 32px;
    margin: 0;
  }
  h1, h2, h3, h4, h5, h6 {
    color: #89b4fa;
    margin-top: 1.4em;
    margin-bottom: 0.4em;
    font-weight: 600;
  }
  h1 { font-size: 2em;   border-bottom: 2px solid #313244; padding-bottom: 0.3em; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #313244; padding-bottom: 0.2em; }
  h3 { font-size: 1.25em; }
  p  { margin: 0.6em 0; }
  a  { color: #89dceb; text-decoration: none; }
  a:hover { text-decoration: underline; }
  strong { color: #f5c2e7; font-weight: 700; }
  em     { color: #f9e2af; font-style: italic; }
  code {
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    background: #313244;
    color: #a6e3a1;
    padding: 2px 6px;
    border-radius: 4px;
  }
  pre {
    background: #11111b;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    margin: 1em 0;
  }
  pre code {
    background: none;
    padding: 0;
    color: #cdd6f4;
    font-size: 0.95em;
  }
  blockquote {
    border-left: 4px solid #89b4fa;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #1e1e2e;
    color: #a6adc8;
    border-radius: 0 6px 6px 0;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
  }
  th, td {
    border: 1px solid #45475a;
    padding: 8px 14px;
    text-align: left;
  }
  th {
    background: #313244;
    color: #89b4fa;
    font-weight: 600;
  }
  tr:nth-child(even) td { background: #1e1e2e; }
  ul, ol { padding-left: 1.6em; margin: 0.5em 0; }
  li { margin: 0.25em 0; }
  hr {
    border: none;
    border-top: 2px solid #313244;
    margin: 1.5em 0;
  }
  del { color: #6c7086; }
  img { max-width: 100%; border-radius: 6px; }
</style>
"""


class MdEditorView:
    """Panel con editor de código MD (izquierda) y preview HTML (derecha)."""

    FONT_MONO = ("Courier New", 11)
    FONT_LNUM = ("Courier New", 11)
    BG_MAIN = "#1e1e2e"
    BG_EDITOR = "#1a1a2a"
    BG_LNUM = "#11111b"
    BG_PANEL = "#2a2a3d"
    FG_TEXT = "#cdd6f4"
    FG_LNUM = "#45475a"
    FG_STATUS = "#a6adc8"
    BTN_BG = "#313244"
    BTN_FG = "#cdd6f4"
    BTN_ACTIVE = "#45475a"

    # Retraso (ms) antes de actualizar el preview tras teclear
    _DEBOUNCE_MS = 300

    def __init__(self, parent: tk.Widget):
        self.frame = tk.Frame(parent, bg=self.BG_MAIN)
        self._controller = None
        self._debounce_id = None
        self._build_ui()

    def set_controller(self, controller):
        self._controller = controller

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        self._build_toolbar()
        self._build_editor_area()
        self._build_statusbar()

    def _build_toolbar(self):
        toolbar = tk.Frame(self.frame, bg=self.BG_PANEL, pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        left = tk.Frame(toolbar, bg=self.BG_PANEL)
        left.pack(side=tk.LEFT, padx=8)

        self._btn(left, "Abrir .md", self._open_file).pack(side=tk.LEFT, padx=3)
        self._btn(left, "Guardar .md", self._save_file).pack(side=tk.LEFT, padx=3)

        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8
        )

        # Inserción rápida de elementos MD comunes
        insert_frame = tk.Frame(toolbar, bg=self.BG_PANEL)
        insert_frame.pack(side=tk.LEFT)

        tk.Label(
            insert_frame,
            text="Insertar:",
            bg=self.BG_PANEL,
            fg=self.FG_STATUS,
            font=("Helvetica", 9),
        ).pack(side=tk.LEFT, padx=(0, 4))

        snippets = [
            ("# H1",        "# Título\n"),
            ("## H2",       "## Subtítulo\n"),
            ("**negrita**", "**texto**"),
            ("*cursiva*",   "*texto*"),
            ("~~tachado~~", "~~texto~~"),
            ("`código`",    "`código`"),
            ("```bloque```","```python\n# código aquí\n```\n"),
            ("> cita",      "> "),
            ("tabla",       "| Col1 | Col2 |\n| --- | --- |\n| a | b |\n"),
            ("enlace",      "[texto](url)"),
            ("imagen",      "![alt](ruta)"),
            ("---",         "\n---\n"),
        ]
        for label, snippet in snippets:
            self._btn(
                insert_frame, label, lambda s=snippet: self._insert_snippet(s),
                font=("Courier New", 8),
            ).pack(side=tk.LEFT, padx=2)

        # Toggle preview
        right = tk.Frame(toolbar, bg=self.BG_PANEL)
        right.pack(side=tk.RIGHT, padx=8)
        self._preview_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            right,
            text="Preview",
            variable=self._preview_var,
            command=self._toggle_preview,
            bg=self.BG_PANEL,
            fg=self.FG_STATUS,
            selectcolor=self.BTN_BG,
            activebackground=self.BTN_ACTIVE,
            font=("Helvetica", 9),
        ).pack(side=tk.RIGHT, padx=4)

    def _build_editor_area(self):
        paned = tk.PanedWindow(
            self.frame,
            orient=tk.HORIZONTAL,
            bg=self.BG_MAIN,
            sashwidth=6,
            sashrelief=tk.FLAT,
        )
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        self._paned = paned

        # --- Panel editor ---
        editor_outer = tk.Frame(paned, bg=self.BG_PANEL)
        editor_outer.columnconfigure(1, weight=1)
        editor_outer.rowconfigure(1, weight=1)

        tk.Label(
            editor_outer,
            text="Editor Markdown",
            bg=self.BG_PANEL,
            fg="#89dceb",
            font=("Helvetica", 11, "bold"),
            anchor=tk.W,
            padx=4,
        ).grid(row=0, column=0, columnspan=3, sticky=tk.EW, pady=(4, 2))

        # Numeración de líneas
        self._line_numbers = tk.Text(
            editor_outer,
            width=4,
            bg=self.BG_LNUM,
            fg=self.FG_LNUM,
            font=self.FONT_LNUM,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=4,
            pady=6,
            wrap=tk.NONE,
            takefocus=False,
        )
        self._line_numbers.grid(row=1, column=0, sticky=tk.NS, pady=(0, 4))

        # Área de texto principal
        self._editor = tk.Text(
            editor_outer,
            bg=self.BG_EDITOR,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            selectbackground="#45475a",
            font=self.FONT_MONO,
            wrap=tk.NONE,
            undo=True,
            relief=tk.FLAT,
            padx=6,
            pady=6,
            tabs=("1c",),
        )
        self._editor.grid(row=1, column=1, sticky=tk.NSEW, pady=(0, 4))
        self._apply_syntax_tags()

        vscroll = ttk.Scrollbar(
            editor_outer, orient=tk.VERTICAL, command=self._sync_scroll_y
        )
        vscroll.grid(row=1, column=2, sticky=tk.NS, pady=(0, 4))
        hscroll = ttk.Scrollbar(
            editor_outer, orient=tk.HORIZONTAL, command=self._editor.xview
        )
        hscroll.grid(row=2, column=0, columnspan=3, sticky=tk.EW)

        self._editor.configure(
            yscrollcommand=lambda *a: (vscroll.set(*a), self._sync_lnum_scroll(*a)),
            xscrollcommand=hscroll.set,
        )
        self._line_numbers.configure(
            yscrollcommand=lambda *a: None
        )

        self._editor.bind("<KeyRelease>", self._on_key_release)
        self._editor.bind("<ButtonRelease>", self._update_status)
        self._editor.bind("<<Modified>>", self._on_modified)
        self._editor.bind("<Control-a>", lambda e: self._select_all())
        self._editor.bind("<Control-A>", lambda e: self._select_all())

        paned.add(editor_outer, minsize=300)

        # --- Panel preview ---
        self._preview_frame = tk.Frame(paned, bg=self.BG_PANEL)
        self._preview_frame.columnconfigure(0, weight=1)
        self._preview_frame.rowconfigure(1, weight=1)

        tk.Label(
            self._preview_frame,
            text="Preview",
            bg=self.BG_PANEL,
            fg="#f38ba8",
            font=("Helvetica", 11, "bold"),
            anchor=tk.W,
            padx=4,
        ).grid(row=0, column=0, sticky=tk.EW, pady=(4, 2))

        self._html_frame = HtmlFrame(
            self._preview_frame,
            messages_enabled=False,
        )
        self._html_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=4, pady=(0, 4))

        paned.add(self._preview_frame, minsize=300)

        # Insertar texto de bienvenida
        self._editor.insert("1.0", _WELCOME_TEXT)
        self._update_line_numbers()
        self._schedule_preview_update()

    def _build_statusbar(self):
        bar = tk.Frame(self.frame, bg=self.BG_PANEL, pady=3)
        bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._status_var = tk.StringVar(value="Listo. | Línea 1, Col 1")
        tk.Label(
            bar,
            textvariable=self._status_var,
            bg=self.BG_PANEL,
            fg=self.FG_STATUS,
            font=("Helvetica", 9),
            anchor=tk.W,
            padx=10,
        ).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # Resaltado de sintaxis básico
    # ------------------------------------------------------------------

    def _apply_syntax_tags(self):
        e = self._editor
        e.tag_configure("heading",   foreground="#89b4fa", font=("Courier New", 12, "bold"))
        e.tag_configure("bold",      foreground="#f5c2e7", font=("Courier New", 11, "bold"))
        e.tag_configure("italic",    foreground="#f9e2af", font=("Courier New", 11, "italic"))
        e.tag_configure("code",      foreground="#a6e3a1", background="#11111b")
        e.tag_configure("codeblock", foreground="#a6e3a1", background="#11111b")
        e.tag_configure("link",      foreground="#89dceb")
        e.tag_configure("quote",     foreground="#a6adc8")
        e.tag_configure("hr",        foreground="#45475a")
        e.tag_configure("list_mark", foreground="#fab387")

    def _highlight_syntax(self):
        import re
        e = self._editor
        # Limpiar todos los tags
        for tag in ("heading", "bold", "italic", "code", "codeblock",
                    "link", "quote", "hr", "list_mark"):
            e.tag_remove(tag, "1.0", tk.END)

        content = e.get("1.0", tk.END)
        lines = content.split("\n")

        in_code_block = False
        for i, line in enumerate(lines):
            lineno = i + 1
            start = f"{lineno}.0"
            end = f"{lineno}.end"

            if line.startswith("```"):
                in_code_block = not in_code_block
                e.tag_add("codeblock", start, end)
                continue

            if in_code_block:
                e.tag_add("codeblock", start, end)
                continue

            # Encabezados
            if re.match(r"^#{1,6}\s", line):
                e.tag_add("heading", start, end)
                continue

            # Blockquote
            if line.startswith("> "):
                e.tag_add("quote", start, end)
                continue

            # Línea horizontal
            if re.match(r"^(\s*[-*_]){3,}\s*$", line):
                e.tag_add("hr", start, end)
                continue

            # Marcadores de lista
            for m in re.finditer(r"^(\s*[*\-+]|\s*\d+\.)\s", line):
                s = f"{lineno}.{m.start()}"
                en = f"{lineno}.{m.end()}"
                e.tag_add("list_mark", s, en)

            # Negrita **...**
            for m in re.finditer(r"\*\*[^*]+\*\*|__[^_]+__", line):
                e.tag_add("bold", f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # Itálica *...*
            for m in re.finditer(r"(?<!\*)\*[^*]+\*(?!\*)|(?<!_)_[^_]+_(?!_)", line):
                e.tag_add("italic", f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # Código inline `...`
            for m in re.finditer(r"`[^`]+`", line):
                e.tag_add("code", f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

            # Enlace [...](...) o imagen
            for m in re.finditer(r"!?\[.*?\]\(.*?\)", line):
                e.tag_add("link", f"{lineno}.{m.start()}", f"{lineno}.{m.end()}")

    # ------------------------------------------------------------------
    # Numeración de líneas
    # ------------------------------------------------------------------

    def _update_line_numbers(self):
        ln = self._line_numbers
        total = int(self._editor.index(tk.END).split(".")[0]) - 1
        ln.configure(state=tk.NORMAL)
        ln.delete("1.0", tk.END)
        ln.insert("1.0", "\n".join(str(i) for i in range(1, total + 1)))
        # Ajustar ancho mínimo
        digits = max(len(str(total)), 3)
        ln.configure(width=digits + 1, state=tk.DISABLED)

    def _sync_scroll_y(self, *args):
        self._editor.yview(*args)
        self._line_numbers.yview(*args)

    def _sync_lnum_scroll(self, first, last):
        self._line_numbers.yview_moveto(first)

    # ------------------------------------------------------------------
    # Preview HTML
    # ------------------------------------------------------------------

    def _schedule_preview_update(self):
        if self._debounce_id:
            self.frame.after_cancel(self._debounce_id)
        self._debounce_id = self.frame.after(self._DEBOUNCE_MS, self._update_preview)

    def _update_preview(self):
        if not self._preview_var.get():
            return
        import markdown as md_lib
        text = self._editor.get("1.0", tk.END)
        html_body = md_lib.markdown(
            text,
            extensions=["tables", "fenced_code", "codehilite", "nl2br", "toc"],
            extension_configs={
                "codehilite": {"css_class": "highlight", "guess_lang": False}
            },
        )
        full_html = f"<html><head>{_PREVIEW_CSS}</head><body>{html_body}</body></html>"
        self._html_frame.load_html(full_html)

    def _toggle_preview(self):
        paned = self._paned
        if self._preview_var.get():
            paned.add(self._preview_frame, minsize=300)
            self._update_preview()
        else:
            paned.forget(self._preview_frame)

    # ------------------------------------------------------------------
    # Eventos y atajos de teclado
    # ------------------------------------------------------------------

    def _select_all(self) -> str:
        self._editor.tag_add(tk.SEL, "1.0", tk.END)
        self._editor.mark_set(tk.INSERT, "1.0")
        self._editor.see(tk.INSERT)
        return "break"

    def _on_key_release(self, _event=None):
        self._update_line_numbers()
        self._highlight_syntax()
        self._schedule_preview_update()
        self._update_status()

    def _on_modified(self, _event=None):
        if self._editor.edit_modified():
            self._update_line_numbers()
            self._highlight_syntax()
            self._schedule_preview_update()
            self._editor.edit_modified(False)

    def _update_status(self, _event=None):
        pos = self._editor.index(tk.INSERT)
        line, col = pos.split(".")
        total_lines = int(self._editor.index(tk.END).split(".")[0]) - 1
        chars = len(self._editor.get("1.0", tk.END)) - 1
        self._status_var.set(
            f"Línea {line}, Col {int(col) + 1}  |  {total_lines} líneas  |  {chars} chars"
        )

    # ------------------------------------------------------------------
    # Snippets / inserción
    # ------------------------------------------------------------------

    def _insert_snippet(self, snippet: str):
        try:
            sel_start = self._editor.index(tk.SEL_FIRST)
            sel_end = self._editor.index(tk.SEL_LAST)
            selected = self._editor.get(sel_start, sel_end)
            # Reemplazar "texto" en el snippet por la selección
            if selected and "texto" in snippet:
                snippet = snippet.replace("texto", selected)
            self._editor.delete(sel_start, sel_end)
            self._editor.insert(sel_start, snippet)
        except tk.TclError:
            self._editor.insert(tk.INSERT, snippet)
        self._on_key_release()

    # ------------------------------------------------------------------
    # Archivo
    # ------------------------------------------------------------------

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Markdown", "*.md *.markdown"), ("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._editor.delete("1.0", tk.END)
            self._editor.insert("1.0", content)
            self._on_key_release()
            self._status_var.set(f"Abierto: {path}")
        except OSError as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e))

    def _save_file(self):
        path = filedialog.asksaveasfilename(
            filetypes=[("Markdown", "*.md"), ("Todos", "*.*")],
            defaultextension=".md",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._editor.get("1.0", tk.END).rstrip("\n"))
            self._status_var.set(f"Guardado: {path}")
        except OSError as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------
    # API pública para el controlador
    # ------------------------------------------------------------------

    def get_text(self) -> str:
        return self._editor.get("1.0", tk.END).rstrip("\n")

    def set_text(self, text: str):
        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", text)
        self._on_key_release()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _btn(self, parent, text, command, font=None, **kwargs):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=kwargs.pop("bg", self.BTN_BG),
            fg=kwargs.pop("fg", self.BTN_FG),
            activebackground=self.BTN_ACTIVE,
            activeforeground=self.BTN_FG,
            relief=tk.FLAT,
            padx=8,
            pady=3,
            cursor="hand2",
            font=font or ("Helvetica", 9),
            **kwargs,
        )


_WELCOME_TEXT = """\
# Bienvenido al editor Markdown

Escribe aquí tu Markdown y verás el resultado a la derecha en tiempo real.

## Elementos básicos

**Negrita** — `**texto**`
*Cursiva* — `*texto*`
~~Tachado~~ — `~~texto~~`
`Código inline` — `` `código` ``

## Bloque de código

Usa triple backtick para bloques multilínea:

```python
def saludar(nombre):
    print(f"Hola, {nombre}!")

saludar("Mundo")
```

```bash
$ echo "Hola desde la terminal"
```

## Listas

- Elemento 1
- Elemento 2
  - Sub-elemento
- Elemento 3

1. Primer paso
2. Segundo paso
3. Tercer paso

## Tabla

| Nombre   | Tipo     | Ejemplo          |
| -------- | -------- | ---------------- |
| Negrita  | Inline   | `**texto**`      |
| Código   | Bloque   | ` ```lang ` |
| Enlace   | Inline   | `[t](url)`       |

## Cita

> "La simplicidad es la máxima sofisticación."
> — Leonardo da Vinci

## Enlace e imagen

[Página de ejemplo](https://example.com)

---

*Usa la barra de herramientas para insertar elementos rápidamente.*
"""
