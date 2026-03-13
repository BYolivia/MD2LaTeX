"""Reglas de sintaxis por lenguaje para el resaltado en la GUI.

Cada LanguageSyntax define qué palabras son keywords (y de qué grupo),
cuál es la sintaxis de comentarios y cuáles son los delimitadores de cadenas.
Estos datos se usan en el resaltado del widget de texto tkinter.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LanguageSyntax:
    """Reglas de sintaxis de un lenguaje para el resaltado en la GUI."""

    # keywords del lenguaje (control flow, declaraciones, etc.)
    keywords: list[str] = field(default_factory=list)
    # palabras clave secundarias: tipos, built-ins, constantes especiales
    keywords2: list[str] = field(default_factory=list)
    # marcadores de comentario de línea, p.ej. ["//", "#"]
    comment_line: list[str] = field(default_factory=list)
    # comentario de bloque como ("/*", "*/"), o None
    comment_block: tuple[str, str] | None = None
    # delimitadores de cadena de texto en orden de preferencia
    string_delimiters: list[str] = field(default_factory=lambda: ['"', "'"])
    # ¿distingue mayúsculas/minúsculas para keywords? (SQL → False)
    case_sensitive: bool = True


# ---------------------------------------------------------------------------
# Datos por lenguaje
# ---------------------------------------------------------------------------

SYNTAX: dict[str, LanguageSyntax] = {

    "python": LanguageSyntax(
        keywords=[
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else",
            "except", "finally", "for", "from", "global", "if", "import",
            "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
            "return", "try", "while", "with", "yield",
        ],
        keywords2=[
            "abs", "all", "any", "bool", "bytes", "callable", "chr", "dict",
            "dir", "divmod", "enumerate", "eval", "exec", "filter", "float",
            "format", "frozenset", "getattr", "globals", "hasattr", "hash",
            "help", "hex", "id", "input", "int", "isinstance", "issubclass",
            "iter", "len", "list", "locals", "map", "max", "min", "next",
            "object", "oct", "open", "ord", "pow", "print", "property",
            "range", "repr", "reversed", "round", "set", "setattr", "slice",
            "sorted", "staticmethod", "str", "sum", "super", "tuple", "type",
            "vars", "zip",
        ],
        comment_line=["#"],
        string_delimiters=['"', "'"],
    ),

    "javascript": LanguageSyntax(
        keywords=[
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "false",
            "finally", "for", "from", "function", "if", "import", "in",
            "instanceof", "let", "new", "null", "of", "return", "static",
            "super", "switch", "this", "throw", "true", "try", "typeof",
            "undefined", "var", "void", "while", "with", "yield",
            "async", "await", "get", "set",
        ],
        keywords2=[
            "Array", "Boolean", "console", "Date", "document", "Error",
            "Function", "JSON", "Math", "Number", "Object", "Promise",
            "Proxy", "Reflect", "RegExp", "Set", "String", "Symbol",
            "Map", "WeakMap", "WeakSet", "window", "globalThis",
            "parseInt", "parseFloat", "isNaN", "isFinite",
            "setTimeout", "setInterval", "clearTimeout", "clearInterval",
            "fetch", "require", "module", "exports",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "'", "`"],
    ),

    "typescript": LanguageSyntax(
        keywords=[
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "enum", "export", "extends",
            "false", "finally", "for", "from", "function", "if", "implements",
            "import", "in", "instanceof", "interface", "let", "namespace",
            "new", "null", "of", "return", "static", "super", "switch", "this",
            "throw", "true", "try", "type", "typeof", "undefined", "var",
            "void", "while", "with", "yield",
            "async", "await", "abstract", "declare", "as", "readonly",
            "keyof", "infer", "is", "override", "satisfies",
        ],
        keywords2=[
            "any", "bigint", "boolean", "never", "number", "object", "string",
            "symbol", "unknown", "Array", "Date", "Error", "Function",
            "Map", "Object", "Promise", "Record", "Set", "Partial",
            "Required", "Readonly", "Pick", "Omit", "Exclude", "Extract",
            "NonNullable", "ReturnType", "InstanceType",
            "console", "Math", "JSON", "parseInt", "parseFloat",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "'", "`"],
    ),

    "go": LanguageSyntax(
        keywords=[
            "break", "case", "chan", "const", "continue", "default", "defer",
            "else", "fallthrough", "for", "func", "go", "goto", "if", "import",
            "interface", "map", "package", "range", "return", "select",
            "struct", "switch", "type", "var", "nil", "true", "false", "iota",
        ],
        keywords2=[
            "append", "cap", "close", "complex", "copy", "delete", "imag",
            "len", "make", "new", "panic", "print", "println", "real",
            "recover", "error",
            "bool", "byte", "complex64", "complex128", "float32", "float64",
            "int", "int8", "int16", "int32", "int64",
            "uint", "uint8", "uint16", "uint32", "uint64", "uintptr",
            "rune", "string",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "`"],
    ),

    "rust": LanguageSyntax(
        keywords=[
            "as", "async", "await", "break", "const", "continue", "crate",
            "dyn", "else", "enum", "extern", "false", "fn", "for", "if",
            "impl", "in", "let", "loop", "match", "mod", "move", "mut",
            "pub", "ref", "return", "self", "Self", "static", "struct",
            "super", "trait", "true", "type", "unsafe", "use", "where", "while",
        ],
        keywords2=[
            "i8", "i16", "i32", "i64", "i128", "isize",
            "u8", "u16", "u32", "u64", "u128", "usize",
            "f32", "f64", "bool", "char", "str", "String",
            "Vec", "Box", "Rc", "Arc", "Cell", "RefCell",
            "Option", "Result", "Some", "None", "Ok", "Err",
            "panic", "todo", "unimplemented", "unreachable",
            "println", "eprintln", "print", "eprint", "format",
            "assert", "assert_eq", "assert_ne", "debug_assert",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"'],
    ),

    "java": LanguageSyntax(
        keywords=[
            "abstract", "assert", "break", "case", "catch", "class", "const",
            "continue", "default", "do", "else", "enum", "extends", "final",
            "finally", "for", "goto", "if", "implements", "import",
            "instanceof", "interface", "native", "new", "package", "private",
            "protected", "public", "return", "static", "strictfp", "super",
            "switch", "synchronized", "this", "throw", "throws", "transient",
            "try", "void", "volatile", "while",
            "true", "false", "null",
        ],
        keywords2=[
            "boolean", "byte", "char", "double", "float", "int", "long", "short",
            "String", "Object", "System", "Math", "Integer", "Long", "Double",
            "Float", "Boolean", "Character", "Byte", "Short",
            "ArrayList", "HashMap", "HashSet", "LinkedList", "List", "Map",
            "Set", "Collection", "Iterator", "Optional",
            "Thread", "Runnable", "Exception", "RuntimeException",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "'"],
    ),

    "sql": LanguageSyntax(
        keywords=[
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE",
            "SET", "DELETE", "CREATE", "TABLE", "ALTER", "DROP", "INDEX",
            "VIEW", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS",
            "ON", "AND", "OR", "NOT", "IN", "BETWEEN", "LIKE", "IS",
            "NULL", "ORDER", "BY", "GROUP", "HAVING", "DISTINCT", "ALL",
            "UNION", "INTERSECT", "EXCEPT", "AS", "CASE", "WHEN", "THEN",
            "ELSE", "END", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
            "CONSTRAINT", "DEFAULT", "UNIQUE", "CHECK", "BEGIN", "COMMIT",
            "ROLLBACK", "TRANSACTION", "WITH", "LIMIT", "OFFSET", "TOP",
            "EXISTS", "ANY", "SOME", "IF", "ELSE", "WHILE", "RETURN",
        ],
        keywords2=[
            "COUNT", "SUM", "AVG", "MAX", "MIN", "COALESCE", "NULLIF",
            "CAST", "CONVERT", "SUBSTRING", "TRIM", "UPPER", "LOWER",
            "LENGTH", "CONCAT", "NOW", "CURRENT_DATE", "CURRENT_TIMESTAMP",
            "ROUND", "FLOOR", "CEIL", "ABS", "MOD",
            "INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT",
            "VARCHAR", "CHAR", "TEXT", "NVARCHAR",
            "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC",
            "DATE", "DATETIME", "TIMESTAMP", "TIME",
            "BOOLEAN", "BOOL", "BIT", "BLOB", "CLOB",
        ],
        comment_line=["--"],
        comment_block=("/*", "*/"),
        string_delimiters=["'"],
        case_sensitive=False,
    ),

    "bash": LanguageSyntax(
        keywords=[
            "if", "then", "else", "elif", "fi", "for", "while", "do", "done",
            "case", "esac", "in", "function", "return", "local", "export",
            "readonly", "declare", "typeset", "unset", "shift", "break",
            "continue", "exit", "trap", "exec", "eval", "source",
            "true", "false",
        ],
        keywords2=[
            # Comandos básicos de bash
            "echo", "printf", "read", "test", "let", "expr", "set", "unset",
            "alias", "unalias", "cd", "pwd", "ls", "mkdir", "rmdir",
            "rm", "cp", "mv", "cat", "grep", "sed", "awk", "find",
            "sort", "head", "tail", "cut", "tr", "wc", "chmod", "chown",
            "chgrp", "kill", "killall", "ps", "top", "env",
            # Privilegios y usuarios
            "sudo", "su",
            # Gestores de paquetes
            "apt", "apt-get", "apt-cache", "dpkg",
            "yum", "dnf", "rpm",
            "pacman", "brew", "snap", "flatpak",
            # Red y transferencia
            "curl", "wget", "ssh", "scp", "rsync",
            "ping", "ifconfig", "ip", "netstat", "ss", "nmap", "hostname",
            # Compresión y archivos
            "tar", "gzip", "gunzip", "zip", "unzip",
            # Herramientas de desarrollo
            "git", "docker", "make",
            # Servicios del sistema
            "systemctl", "service", "journalctl", "crontab", "at",
            # Información del sistema
            "uname", "df", "du", "free", "mount", "umount",
            "lsblk", "fdisk", "mkfs",
            # Utilidades
            "touch", "ln", "which", "whereis", "man", "help",
            "history", "xargs", "tee", "date", "time", "sleep",
            "basename", "dirname",
        ],
        comment_line=["#"],
        string_delimiters=['"', "'"],
    ),

    # sh: bash + comandos de administración del sistema
    "sh": LanguageSyntax(
        keywords=[
            "if", "then", "else", "elif", "fi", "for", "while", "do", "done",
            "case", "esac", "in", "function", "return", "local", "export",
            "readonly", "declare", "typeset", "unset", "shift", "break",
            "continue", "exit", "trap", "exec", "eval", "source",
            "true", "false",
        ],
        keywords2=[
            # Comandos básicos de bash
            "echo", "printf", "read", "test", "let", "expr", "set",
            "alias", "unalias", "cd", "pwd", "ls", "mkdir", "rmdir",
            "rm", "cp", "mv", "cat", "grep", "sed", "awk", "find",
            "sort", "head", "tail", "cut", "tr", "wc", "chmod", "chown",
            "chgrp", "kill", "killall", "ps", "top", "env",
            # Privilegios y usuarios
            "sudo", "su",
            # Gestores de paquetes
            "apt", "apt-get", "apt-cache", "dpkg",
            "yum", "dnf", "rpm",
            "pacman", "brew", "snap", "flatpak",
            # Red y transferencia
            "curl", "wget", "ssh", "scp", "rsync",
            "ping", "ifconfig", "ip", "netstat", "ss", "nmap", "hostname",
            # Compresión y archivos
            "tar", "gzip", "gunzip", "zip", "unzip",
            # Herramientas de desarrollo
            "git", "docker", "make",
            # Servicios del sistema
            "systemctl", "service", "journalctl", "crontab", "at",
            # Información del sistema
            "uname", "df", "du", "free", "mount", "umount",
            "lsblk", "fdisk", "mkfs",
            # Utilidades
            "touch", "ln", "which", "whereis", "man", "help",
            "history", "xargs", "tee", "date", "time", "sleep",
            "basename", "dirname",
        ],
        comment_line=["#"],
        string_delimiters=['"', "'"],
    ),

    "kotlin": LanguageSyntax(
        keywords=[
            "abstract", "actual", "annotation", "as", "break", "by", "catch",
            "class", "companion", "const", "constructor", "continue",
            "crossinline", "data", "do", "dynamic", "else", "enum", "expect",
            "external", "false", "final", "finally", "for", "fun", "get",
            "if", "import", "in", "infix", "init", "inline", "inner",
            "interface", "internal", "is", "it", "lateinit", "noinline",
            "null", "object", "open", "operator", "out", "override",
            "package", "private", "protected", "public", "reified", "return",
            "sealed", "set", "super", "suspend", "tailrec", "this", "throw",
            "true", "try", "typealias", "val", "var", "vararg", "when",
            "where", "while",
        ],
        keywords2=[
            "Any", "Array", "Boolean", "Byte", "Char", "Double", "Float",
            "Int", "Long", "Nothing", "Number", "Short", "String", "Unit",
            "List", "MutableList", "Map", "MutableMap", "Set", "MutableSet",
            "Pair", "Triple", "Collection", "Sequence",
            "println", "print", "readLine", "TODO",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "'"],
    ),

    "dart": LanguageSyntax(
        keywords=[
            "abstract", "as", "assert", "async", "await", "break", "case",
            "catch", "class", "const", "continue", "covariant", "default",
            "deferred", "do", "dynamic", "else", "enum", "export", "extends",
            "extension", "external", "factory", "false", "final", "finally",
            "for", "get", "hide", "if", "implements", "import", "in",
            "interface", "is", "late", "library", "mixin", "new", "null",
            "on", "operator", "part", "required", "rethrow", "return", "set",
            "show", "static", "super", "switch", "sync", "this", "throw",
            "true", "try", "typedef", "var", "void", "while", "with", "yield",
        ],
        keywords2=[
            "bool", "double", "int", "num", "String", "Object", "dynamic",
            "List", "Map", "Set", "Future", "Stream", "Iterable",
            "print", "assert",
        ],
        comment_line=["//"],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "'"],
    ),

    "json": LanguageSyntax(
        keywords=["true", "false", "null"],
        comment_line=[],
        string_delimiters=['"'],
    ),

    "yaml": LanguageSyntax(
        keywords=["true", "false", "null", "yes", "no", "on", "off"],
        comment_line=["#"],
        string_delimiters=['"', "'"],
    ),

    "css": LanguageSyntax(
        keywords=[
            "important", "inherit", "initial", "unset", "auto", "none",
            "normal", "bold", "italic", "underline", "hidden", "visible",
            "solid", "dashed", "dotted", "flex", "grid", "block", "inline",
            "absolute", "relative", "fixed", "sticky", "static",
        ],
        comment_block=("/*", "*/"),
        string_delimiters=['"', "'"],
    ),

    "dockerfile": LanguageSyntax(
        keywords=[
            "FROM", "RUN", "CMD", "LABEL", "EXPOSE", "ENV", "ADD", "COPY",
            "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG", "ONBUILD",
            "STOPSIGNAL", "HEALTHCHECK", "SHELL", "MAINTAINER", "AS",
        ],
        comment_line=["#"],
        string_delimiters=['"', "'"],
    ),

    "toml": LanguageSyntax(
        keywords=["true", "false"],
        comment_line=["#"],
        string_delimiters=['"', "'"],
    ),

    "graphql": LanguageSyntax(
        keywords=[
            "query", "mutation", "subscription", "fragment", "on", "type",
            "input", "interface", "union", "enum", "scalar", "schema",
            "directive", "extend", "implements", "true", "false", "null",
        ],
        comment_line=["#"],
        string_delimiters=['"'],
    ),
}

# ---------------------------------------------------------------------------
# Aliases (equivalentes de latex_languages._CUSTOM_ALIASES + extras)
# ---------------------------------------------------------------------------

_ALIASES: dict[str, str] = {
    # JavaScript
    "js": "javascript", "jsx": "javascript", "mjs": "javascript",
    # TypeScript
    "ts": "typescript", "tsx": "typescript",
    # Go
    "golang": "go",
    # Rust
    "rs": "rust",
    # Kotlin
    "kt": "kotlin", "kts": "kotlin",
    # Python
    "py": "python", "python3": "python",
    # Shell
    "shell": "bash", "zsh": "bash",
    # SQL
    "mysql": "sql", "postgresql": "sql", "sqlite": "sql",
}


def get_syntax(lang: str) -> LanguageSyntax | None:
    """Devuelve la sintaxis para un lenguaje dado, o None si no se conoce."""
    key = lang.lower().strip()
    key = _ALIASES.get(key, key)
    return SYNTAX.get(key)


def normalize_lang(lang: str) -> str:
    """Normaliza el nombre de un lenguaje a su clave canónica."""
    key = lang.lower().strip()
    return _ALIASES.get(key, key)
