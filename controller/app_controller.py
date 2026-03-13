"""Controlador principal de la aplicación."""
from __future__ import annotations

from pathlib import Path

from model.converter import Converter
from model.language_color_config import (
    LanguageColorConfig,
    COLORS_FOLDER,
    create_default_configs,
)
from view.main_window import MainWindow


class AppController:
    """Coordina la vista y el modelo sin que ninguno conozca al otro."""

    MD_FILETYPES = [("Markdown", "*.md *.markdown"), ("Texto", "*.txt"), ("Todos", "*.*")]
    LATEX_FILETYPES = [("LaTeX", "*.tex"), ("Todos", "*.*")]
    HTML_FILETYPES = [("HTML", "*.html *.htm"), ("Todos", "*.*")]

    def __init__(self, view: MainWindow):
        self._view = view
        self._model = Converter()
        create_default_configs()          # crea JSONs por defecto si no existen
        view.set_controller(self)
        view.lang_colors_tab.set_controller(self)  # conectar la pestaña de colores

    # ------------------------------------------------------------------
    # Acciones de conversión MD ↔ LaTeX
    # ------------------------------------------------------------------

    def convert_md_to_latex(self):
        try:
            md_text = self._view.get_md_text()
            if not md_text.strip():
                self._view.set_status("El panel de Markdown está vacío.")
                return
            color_configs = LanguageColorConfig.load_all()
            result = self._model.md_to_latex(md_text, color_configs=color_configs)
            self._view.set_latex_text(result.body)
            self._view.set_preamble(result.preamble_imports, result.preamble_config)
            self._view.set_status("Conversión MD → LaTeX completada.")
        except Exception as e:
            self._view.show_error("Error de conversión", str(e))
            self._view.set_status(f"Error: {e}")

    def convert_latex_to_md(self):
        try:
            latex_text = self._view.get_latex_text()
            if not latex_text.strip():
                self._view.set_status("El panel de LaTeX está vacío.")
                return
            result = self._model.latex_to_md(latex_text)
            self._view.set_md_text(result)
            self._view.set_status("Conversión LaTeX → MD completada.")
        except Exception as e:
            self._view.show_error("Error de conversión", str(e))
            self._view.set_status(f"Error: {e}")

    # ------------------------------------------------------------------
    # Operaciones de archivo
    # ------------------------------------------------------------------

    def open_file(self, fmt: str):
        filetypes = self.MD_FILETYPES if fmt == "md" else self.LATEX_FILETYPES
        path = self._view.ask_open_file(filetypes)
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if fmt == "md":
                self._view.set_md_text(content)
            else:
                self._view.set_latex_text(content)
            self._view.set_status(f"Archivo cargado: {path}")
        except OSError as e:
            self._view.show_error("Error al abrir archivo", str(e))
            self._view.set_status(f"Error al abrir: {e}")

    def save_file(self, fmt: str):
        filetypes = self.MD_FILETYPES if fmt == "md" else self.LATEX_FILETYPES
        ext = ".md" if fmt == "md" else ".tex"
        path = self._view.ask_save_file(filetypes, ext)
        if not path:
            return
        try:
            content = self._view.get_md_text() if fmt == "md" else self._view.get_latex_text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._view.set_status(f"Archivo guardado: {path}")
        except OSError as e:
            self._view.show_error("Error al guardar archivo", str(e))
            self._view.set_status(f"Error al guardar: {e}")

    # ------------------------------------------------------------------
    # Acciones MD → HTML
    # ------------------------------------------------------------------

    def convert_md_to_html(self):
        try:
            md_text = self._view.get_html_md_text()
            if not md_text.strip():
                self._view.set_html_status("El panel de Markdown está vacío.")
                return
            result = self._model.md_to_html(md_text, full_document=True)
            self._view.set_html_out_text(result)
            self._view.set_html_status("Conversión MD → HTML completada.")
        except Exception as e:
            self._view.show_error("Error de conversión", str(e))
            self._view.set_html_status(f"Error: {e}")

    def convert_html_to_md(self):
        try:
            html_text = self._view.get_html_out_text()
            if not html_text.strip():
                self._view.set_html_status("El panel de HTML está vacío.")
                return
            result = self._model.html_to_md(html_text)
            self._view.set_html_md_text(result)
            self._view.set_html_status("Conversión HTML → MD completada.")
        except Exception as e:
            self._view.show_error("Error de conversión", str(e))
            self._view.set_html_status(f"Error: {e}")

    def open_html_md_file(self):
        path = self._view.ask_open_file(self.MD_FILETYPES)
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._view.set_html_md_text(content)
            self._view.set_html_status(f"Archivo cargado: {path}")
        except OSError as e:
            self._view.show_error("Error al abrir archivo", str(e))

    def open_html_file(self):
        path = self._view.ask_open_file(self.HTML_FILETYPES)
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._view.set_html_out_text(content)
            self._view.set_html_status(f"Archivo cargado: {path}")
        except OSError as e:
            self._view.show_error("Error al abrir archivo", str(e))

    def save_html_md_file(self):
        path = self._view.ask_save_file(self.MD_FILETYPES, ".md")
        if not path:
            return
        try:
            content = self._view.get_html_md_text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._view.set_html_status(f"Archivo guardado: {path}")
        except OSError as e:
            self._view.show_error("Error al guardar archivo", str(e))

    def save_html_file(self):
        path = self._view.ask_save_file(self.HTML_FILETYPES, ".html")
        if not path:
            return
        try:
            content = self._view.get_html_out_text()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._view.set_html_status(f"Archivo guardado: {path}")
        except OSError as e:
            self._view.show_error("Error al guardar archivo", str(e))

    # ------------------------------------------------------------------
    # Operaciones del editor de colores
    # ------------------------------------------------------------------

    def get_color_configs(self) -> dict[str, LanguageColorConfig]:
        return LanguageColorConfig.load_all()

    def save_color_config(self, config: LanguageColorConfig) -> str:
        path = config.save()
        # Recargar configs en todos los paneles para que los colores se reflejen de inmediato
        self._view.reload_code_configs()
        return str(path)

    def delete_color_config(self, language: str) -> bool:
        return LanguageColorConfig.delete(language)

    def get_colors_folder(self) -> Path:
        return COLORS_FOLDER
