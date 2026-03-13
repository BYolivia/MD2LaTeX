"""Conversor de HTML a Markdown usando html.parser de stdlib."""

from html.parser import HTMLParser
import re


class HtmlToMdConverter(HTMLParser):
    """Convierte HTML a Markdown.

    Elementos soportados:
    h1-h6, p, br, hr, strong/b, em/i, s/del/strike, code, pre,
    ul/ol/li (anidados), blockquote, a, img, table.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)

    def convert(self, html: str) -> str:
        # Pila de buffers de salida (para capturar celdas de tabla y blockquotes)
        self._bufs: list[list[str]] = [[]]
        self._pend: list[int] = [0]   # newlines pendientes por buffer

        self._stack: list[str] = []   # pila de tags HTML
        self._list_stack: list[tuple] = []  # ('ul'/'ol', contador)
        self._in_pre: int = 0
        self._in_code: int = 0
        self._skip: int = 0           # contador de tags a ignorar
        self._href: str | None = None
        self._tables: list[dict] = []

        self.feed(html)

        result = ''.join(self._bufs[0]).strip()
        return re.sub(r'\n{3,}', '\n\n', result)

    # ── Helpers de buffer ──────────────────────────────────────────────

    def _emit(self, text: str) -> None:
        if not text:
            return
        nl = self._pend[-1]
        if nl and self._bufs[-1]:
            self._bufs[-1].append('\n' * nl)
        self._pend[-1] = 0
        self._bufs[-1].append(text)

    def _nl(self, n: int = 1) -> None:
        """Solicita al menos N newlines antes del próximo texto."""
        if self._pend[-1] < n:
            self._pend[-1] = n

    def _push(self) -> None:
        """Inicia un nuevo buffer de captura."""
        self._bufs.append([])
        self._pend.append(0)

    def _pop(self) -> str:
        """Finaliza el buffer de captura y devuelve su contenido."""
        content = ''.join(self._bufs.pop()).strip()
        self._pend.pop()
        return content

    # ── Callbacks HTMLParser ───────────────────────────────────────────

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs = dict(attrs)

        if tag in ('head', 'style', 'script'):
            self._skip += 1
            return
        if self._skip:
            return

        self._stack.append(tag)

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._nl(2)
            self._emit('#' * int(tag[1]) + ' ')

        elif tag == 'p':
            self._nl(2)

        elif tag == 'br':
            self._emit('  \n')

        elif tag == 'hr':
            self._nl(2)
            self._emit('---')
            self._nl(2)

        elif tag in ('strong', 'b'):
            self._emit('**')

        elif tag in ('em', 'i'):
            self._emit('*')

        elif tag in ('s', 'del', 'strike'):
            self._emit('~~')

        elif tag == 'code':
            if self._in_pre:
                # Intentar extraer lenguaje del class para el bloque de código
                m = re.search(r'(?:language|lang)-(\w+)', attrs.get('class', ''), re.I)
                if m and self._bufs[-1] and self._bufs[-1][-1].endswith('```\n'):
                    # Insertar el lenguaje en la última línea de apertura del bloque
                    self._bufs[-1][-1] = f'```{m.group(1)}\n'
            else:
                self._emit('`')
            self._in_code += 1

        elif tag == 'pre':
            self._in_pre += 1
            self._nl(2)
            # Intentar extraer lenguaje del class del propio pre
            m = re.search(r'(?:language|lang)-(\w+)', attrs.get('class', ''), re.I)
            lang = m.group(1) if m else ''
            self._emit(f'```{lang}\n')

        elif tag == 'ul':
            self._list_stack.append(('ul', 0))
            self._nl(2)

        elif tag == 'ol':
            self._list_stack.append(('ol', 0))
            self._nl(2)

        elif tag == 'li':
            self._nl(1)
            if self._list_stack:
                kind, num = self._list_stack[-1]
                indent = '  ' * (len(self._list_stack) - 1)
                if kind == 'ul':
                    self._emit(indent + '- ')
                else:
                    num += 1
                    self._list_stack[-1] = (kind, num)
                    self._emit(indent + f'{num}. ')

        elif tag == 'blockquote':
            self._nl(2)
            self._push()

        elif tag == 'a':
            self._href = attrs.get('href', '')
            self._emit('[')

        elif tag == 'img':
            alt = attrs.get('alt', '')
            src = attrs.get('src', '')
            self._emit(f'![{alt}]({src})')

        elif tag == 'table':
            self._nl(2)
            self._tables.append({'rows': [], 'cur': None, 'hdr': False})

        elif tag == 'thead':
            if self._tables:
                self._tables[-1]['hdr'] = True

        elif tag == 'tbody':
            if self._tables:
                self._tables[-1]['hdr'] = False

        elif tag == 'tr':
            if self._tables:
                t = self._tables[-1]
                t['cur'] = []
                t['cur_hdr'] = t['hdr']

        elif tag in ('th', 'td'):
            if self._tables and self._tables[-1].get('cur') is not None:
                self._push()
                if tag == 'th':
                    self._tables[-1]['cur_hdr'] = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ('head', 'style', 'script'):
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return

        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._nl(2)

        elif tag == 'p':
            self._nl(2)

        elif tag in ('strong', 'b'):
            self._emit('**')

        elif tag in ('em', 'i'):
            self._emit('*')

        elif tag in ('s', 'del', 'strike'):
            self._emit('~~')

        elif tag == 'code':
            self._in_code = max(0, self._in_code - 1)
            if not self._in_pre:
                self._emit('`')

        elif tag == 'pre':
            self._in_pre = max(0, self._in_pre - 1)
            self._emit('```')
            self._nl(2)

        elif tag in ('ul', 'ol'):
            if self._list_stack:
                self._list_stack.pop()
            self._nl(2)

        elif tag == 'li':
            self._nl(1)

        elif tag == 'blockquote':
            content = self._pop()
            quoted = '\n'.join('> ' + line for line in content.split('\n'))
            self._emit(quoted)
            self._nl(2)

        elif tag == 'a':
            self._emit(f']({self._href or ""})')
            self._href = None

        elif tag in ('th', 'td'):
            if self._tables and self._tables[-1].get('cur') is not None:
                self._tables[-1]['cur'].append(self._pop())

        elif tag == 'tr':
            if self._tables:
                t = self._tables[-1]
                if t.get('cur') is not None:
                    t['rows'].append({'cells': t['cur'], 'hdr': t.get('cur_hdr', False)})
                    t['cur'] = None

        elif tag == 'table':
            if self._tables:
                self._render_table(self._tables.pop())
                self._nl(2)

    def handle_data(self, data: str) -> None:
        if self._skip:
            return

        if self._in_pre:
            # En bloques pre preservar el texto tal cual
            self._bufs[-1].append(data)
            return

        # Normalizar espacios en blanco
        text = re.sub(r'[ \t\r\n]+', ' ', data)
        if text.strip():
            self._emit(text)
        elif (text == ' '
              and self._pend[-1] == 0  # no hay salto de bloque pendiente
              and self._bufs[-1]
              and not self._bufs[-1][-1].endswith((' ', '\n'))):
            self._emit(' ')

    def _render_table(self, t: dict) -> None:
        rows = t['rows']
        if not rows:
            return

        ncols = max(len(r['cells']) for r in rows)

        def fmt(cells: list) -> str:
            padded = list(cells) + [''] * (ncols - len(cells))
            return '| ' + ' | '.join(c.replace('|', '\\|') for c in padded) + ' |'

        lines = [
            fmt(rows[0]['cells']),
            '| ' + ' | '.join(['---'] * ncols) + ' |',
        ]
        for row in rows[1:]:
            lines.append(fmt(row['cells']))

        self._emit('\n'.join(lines))
