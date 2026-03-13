"""Fachada del modelo de conversión."""

import markdown as _md_lib

from model.md_to_latex import MdToLatexConverter, ConversionResult
from model.latex_to_md import LatexToMdConverter
from model.html_to_md import HtmlToMdConverter

_MD_EXTENSIONS = ["tables", "fenced_code", "codehilite", "nl2br", "toc", "attr_list"]
_MD_EXT_CONFIG = {
    "codehilite": {"css_class": "highlight", "guess_lang": False}
}


class Converter:
    """Punto de entrada único para las conversiones."""

    def __init__(self):
        self._md_to_latex = MdToLatexConverter()
        self._latex_to_md = LatexToMdConverter()
        self._html_to_md = HtmlToMdConverter()

    def md_to_latex(self, text: str, color_configs: dict | None = None) -> ConversionResult:
        return self._md_to_latex.convert(text, color_configs=color_configs)

    def latex_to_md(self, text: str) -> str:
        return self._latex_to_md.convert(text)

    def html_to_md(self, html: str) -> str:
        """Convierte HTML a Markdown."""
        return self._html_to_md.convert(html)

    def md_to_html(self, text: str, full_document: bool = False) -> str:
        """Convierte Markdown a HTML.

        Args:
            text: Texto Markdown.
            full_document: Si True, devuelve un documento HTML completo con
                           DOCTYPE, <head> y <body>. Si False, solo el fragmento.
        """
        body = _md_lib.markdown(
            text,
            extensions=_MD_EXTENSIONS,
            extension_configs=_MD_EXT_CONFIG,
        )
        if not full_document:
            return body
        return (
            "<!DOCTYPE html>\n"
            "<html lang=\"es\">\n"
            "<head>\n"
            "  <meta charset=\"UTF-8\">\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "  <title>Documento</title>\n"
            "  <style>\n"
            "    body { font-family: sans-serif; max-width: 800px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }\n"
            "    pre { background: #f4f4f4; padding: 1em; border-radius: 4px; overflow-x: auto; }\n"
            "    code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }\n"
            "    table { border-collapse: collapse; width: 100%; }\n"
            "    th, td { border: 1px solid #ddd; padding: 8px; }\n"
            "    th { background: #f0f0f0; }\n"
            "    blockquote { border-left: 4px solid #ccc; margin: 0; padding-left: 1em; color: #666; }\n"
            "  </style>\n"
            "</head>\n"
            f"<body>\n{body}\n</body>\n"
            "</html>"
        )
