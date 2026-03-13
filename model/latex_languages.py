"""
Soporte de lenguajes para el entorno lstlisting de LaTeX.

Distingue entre lenguajes nativos del paquete listings y lenguajes que
necesitan una definición personalizada (lstdefinelanguage).
"""
from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Lenguajes soportados de forma nativa por el paquete listings
# Clave: nombre normalizado (lowercase sin puntuación especial)
# Valor: nombre exacto que acepta listings (sensible a mayúsculas)
# ---------------------------------------------------------------------------
_NATIVE: dict[str, str] = {
    # Shells / scripting
    "bash": "bash",
    "sh": "Sh",
    "shell": "bash",
    "zsh": "bash",
    "csh": "csh",
    "ksh": "ksh",
    # C / C++
    "c": "C",
    "cpp": "C++",
    "c++": "C++",
    "cxx": "C++",
    # JVM
    "java": "Java",
    "scala": "Scala",
    # .NET
    "csharp": "C",          # listings no tiene C# nativo; se aproxima con C
    "fsharp": "FSharp",
    "vbscript": "VBScript",
    # Python
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    # Web (solo markup)
    "html": "HTML",
    "xml": "XML",
    "xslt": "XSLT",
    # Bases de datos
    "sql": "SQL",
    "sparql": "SPARQL",
    # Funcionales / otros
    "haskell": "Haskell",
    "ocaml": "Caml",
    "caml": "Caml",
    "erlang": "erlang",
    "lisp": "Lisp",
    "ml": "ML",
    "prolog": "Prolog",
    "lua": "Lua",
    "perl": "Perl",
    "php": "PHP",
    "ruby": "Ruby",
    "rb": "Ruby",
    "r": "R",
    "matlab": "Matlab",
    "octave": "Octave",
    "fortran": "Fortran",
    "pascal": "Pascal",
    "delphi": "Delphi",
    "ada": "Ada",
    "cobol": "Cobol",
    "verilog": "Verilog",
    "vhdl": "VHDL",
    "tcl": "tcl",
    "awk": "Awk",
    "make": "make",
    "gnuplot": "Gnuplot",
    "tex": "TeX",
    "postscript": "PostScript",
    "mathematica": "Mathematica",
    "scilab": "Scilab",
    "sas": "SAS",
    "rexx": "Rexx",
    "logo": "Logo",
    "swift": "Swift",
    "llvm": "LLVM",
}

# ---------------------------------------------------------------------------
# Definiciones custom para lenguajes no soportados de forma nativa
# ---------------------------------------------------------------------------
_CUSTOM: dict[str, str] = {

    "javascript": r"""
\lstdefinelanguage{JavaScript}{
  keywords={break,case,catch,class,const,continue,debugger,default,delete,
    do,else,export,extends,false,finally,for,from,function,if,import,in,
    instanceof,let,new,null,of,return,static,super,switch,this,throw,true,
    try,typeof,undefined,var,void,while,with,yield,async,await,get,set},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  morestring=[b]`,
  sensitive=true,
}""",

    "typescript": r"""
\lstdefinelanguage{TypeScript}{
  keywords={break,case,catch,class,const,continue,debugger,default,delete,
    do,else,enum,export,extends,false,finally,for,from,function,if,implements,
    import,in,instanceof,interface,let,namespace,new,null,of,return,static,
    super,switch,this,throw,true,try,type,typeof,undefined,var,void,while,
    with,yield,async,await,abstract,declare,as,readonly,keyof,infer,is,
    override,satisfies},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  morestring=[b]`,
  sensitive=true,
}""",

    "go": r"""
\lstdefinelanguage{Go}{
  keywords={break,case,chan,const,continue,default,defer,else,fallthrough,
    for,func,go,goto,if,import,interface,map,package,range,return,select,
    struct,switch,type,var,nil,true,false,iota,make,new,len,cap,append,
    copy,delete,close,panic,recover,print,println,error},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]",
  morestring=[b]`,
  sensitive=true,
}""",

    "rust": r"""
\lstdefinelanguage{Rust}{
  keywords={as,async,await,break,const,continue,crate,dyn,else,enum,extern,
    false,fn,for,if,impl,in,let,loop,match,mod,move,mut,pub,ref,return,
    self,Self,static,struct,super,trait,true,type,unsafe,use,where,while},
  morekeywords=[2]{i8,i16,i32,i64,i128,isize,u8,u16,u32,u64,u128,usize,
    f32,f64,bool,char,str,String,Vec,Option,Result,Some,None,Ok,Err,
    Box,Rc,Arc,Cell,RefCell},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]",
  sensitive=true,
}""",

    "kotlin": (
        r"\lstdefinelanguage{Kotlin}{" "\n"
        r"  keywords={abstract,actual,annotation,as,break,by,catch,class,companion," "\n"
        r"    const,constructor,continue,crossinline,data,do,dynamic,else," "\n"
        r"    enum,expect,external,false,final,finally,for,fun,get,if," "\n"
        r"    import,in,infix,init,inline,inner,interface,internal,is,it,lateinit," "\n"
        r"    noinline,null,object,open,operator,out,override,package,private," "\n"
        r"    protected,public,reified,return,sealed,set," "\n"
        r"    super,suspend,tailrec,this,throw,true,try,typealias,val," "\n"
        r"    var,vararg,when,where,while}," "\n"
        r"  comment=[l]{//}," "\n"
        r"  morecomment=[s]{/*}{*/}," "\n"
        r"  morestring=[b]'," "\n"
        r'  morestring=[b]",' "\n"
        r'  morestring=[s]{"""}{"""},' "\n"
        r"  sensitive=true," "\n"
        r"}"
    ),

    "dart": r"""
\lstdefinelanguage{Dart}{
  keywords={abstract,as,assert,async,await,break,case,catch,class,const,
    continue,covariant,default,deferred,do,dynamic,else,enum,export,extends,
    extension,external,factory,false,final,finally,for,Function,get,hide,
    if,implements,import,in,interface,is,late,library,mixin,new,null,on,
    operator,part,required,rethrow,return,set,show,static,super,switch,sync,
    this,throw,true,try,typedef,var,void,while,with,yield},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  sensitive=true,
}""",

    "json": r"""
\lstdefinelanguage{JSON}{
  keywords={true,false,null},
  morestring=[b]",
  sensitive=true,
}""",

    "yaml": r"""
\lstdefinelanguage{YAML}{
  keywords={true,false,null,yes,no,on,off},
  comment=[l]{\#},
  morestring=[b]',
  morestring=[b]",
  sensitive=true,
}""",

    "css": r"""
\lstdefinelanguage{CSS}{
  keywords={color,background,margin,padding,border,font,display,position,
    top,left,right,bottom,width,height,max,min,flex,grid,transform,
    transition,animation,overflow,opacity,z-index,cursor,content,
    box-shadow,text-align,font-size,font-weight,line-height,list-style,
    text-decoration,visibility,float,clear},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  sensitive=false,
}""",

    "dockerfile": r"""
\lstdefinelanguage{Dockerfile}{
  keywords={FROM,RUN,CMD,LABEL,EXPOSE,ENV,ADD,COPY,ENTRYPOINT,VOLUME,
    USER,WORKDIR,ARG,ONBUILD,STOPSIGNAL,HEALTHCHECK,SHELL,MAINTAINER,
    AS,to},
  comment=[l]{\#},
  morestring=[b]',
  morestring=[b]",
  sensitive=true,
}""",

    "toml": (
        r"\lstdefinelanguage{TOML}{" "\n"
        r"  keywords={true,false,nan,inf}," "\n"
        r"  comment=[l]{\#}," "\n"
        r"  morestring=[b]'," "\n"
        r'  morestring=[b]",' "\n"
        r'  morestring=[s]{"""}{"""},' "\n"
        r"  morestring=[s]{'''}{'''}," "\n"
        r"  sensitive=true," "\n"
        r"}"
    ),

    "graphql": (
        r"\lstdefinelanguage{GraphQL}{" "\n"
        r"  keywords={query,mutation,subscription,fragment,on,type,input,interface," "\n"
        r"    union,enum,scalar,schema,directive,extend,implements,true,false,null}," "\n"
        r"  comment=[l]{\#}," "\n"
        r'  morestring=[b]",' "\n"
        r'  morestring=[s]{"""}{"""},' "\n"
        r"  sensitive=true," "\n"
        r"}"
    ),
}

# Alias de lenguajes custom hacia su clave normalizada
_CUSTOM_ALIASES: dict[str, str] = {
    "js": "javascript",
    "jsx": "javascript",
    "mjs": "javascript",
    "ts": "typescript",
    "tsx": "typescript",
    "golang": "go",
    "rs": "rust",
    "kt": "kotlin",
    "kts": "kotlin",
}

# ── Importaciones necesarias ──────────────────────────────────────────
_IMPORTS = r"""\usepackage{listings}
\usepackage{xcolor}"""

# ── Configuración general de listings ─────────────────────────────────
_BASE_CONFIG = r"""\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  breakatwhitespace=false,
  numbers=left,
  numberstyle=\tiny\color{gray},
  numbersep=8pt,
  frame=single,
  framesep=4pt,
  tabsize=2,
  showstringspaces=false,
  captionpos=b,
  keepspaces=true,
  columns=flexible,
}"""


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

@dataclass
class LanguageInfo:
    """Resultado del análisis de un lenguaje de código."""
    listings_name: str          # Nombre a usar en \begin{lstlisting}[language=...]
    is_native: bool             # True: soportado por listings sin definición extra
    custom_definition: str = "" # Código lstdefinelanguage si no es nativo


def resolve_language(lang: str) -> LanguageInfo:
    """Resuelve el nombre de un lenguaje MD al equivalente para listings.

    Returns:
        LanguageInfo con el nombre a usar y si necesita definición custom.
    """
    key = lang.lower().strip()

    # Alias custom
    key = _CUSTOM_ALIASES.get(key, key)

    # Nativo
    if key in _NATIVE:
        return LanguageInfo(listings_name=_NATIVE[key], is_native=True)

    # Custom con definición
    if key in _CUSTOM:
        # El nombre en listings será la versión capitalizada de la clave
        listings_name = key.capitalize()
        return LanguageInfo(
            listings_name=listings_name,
            is_native=False,
            custom_definition=_CUSTOM[key],
        )

    # Desconocido: usar sin resaltado (listings permite lenguaje vacío)
    return LanguageInfo(listings_name="", is_native=True)


def _generate_lstdefinelanguage(cfg: "LanguageColorConfig", key: str) -> str:
    """Genera \\lstdefinelanguage desde las reglas sintácticas del LanguageColorConfig.

    Produce una definición completa de lenguaje (keywords, comentarios, strings)
    a partir de los datos que el usuario configuró en el JSON, sin colores
    hardcodeados (los colores van en \\lstdefinestyle).
    """
    # Nombre de display del lenguaje en listings
    _DISPLAY = {
        "javascript": "JavaScript", "typescript": "TypeScript",
        "go": "Go",    "rust": "Rust",    "kotlin": "Kotlin",
        "dart": "Dart", "json": "JSON",   "yaml": "YAML",
        "css": "CSS",  "dockerfile": "Dockerfile",
        "toml": "TOML", "graphql": "GraphQL",
    }
    lang_display = _DISPLAY.get(key, key.capitalize())

    lines = [f"\\lstdefinelanguage{{{lang_display}}}{{"]

    if cfg.keywords_list:
        kw_csv = ",".join(cfg.keywords_list)
        lines.append(f"  keywords={{{kw_csv}}},")

    if cfg.keywords2_list:
        kw2_csv = ",".join(cfg.keywords2_list)
        lines.append(f"  morekeywords=[2]{{{kw2_csv}}},")

    for marker in cfg.comment_line:
        # '#' debe escaparse en LaTeX como \#
        escaped = marker.replace("#", "\\#")
        lines.append(f"  comment=[l]{{{escaped}}},")

    if cfg.comment_block_open and cfg.comment_block_close:
        lines.append(
            f"  morecomment=[s]{{{cfg.comment_block_open}}}"
            f"{{{cfg.comment_block_close}}},"
        )

    for delim in cfg.string_delimiters:
        lines.append(f"  morestring=[b]{delim},")

    lines.append(f"  sensitive={'true' if cfg.case_sensitive else 'false'},")
    lines.append("}")
    return "\n".join(lines)


def build_preamble(
    languages: set[str],
    color_configs: "dict | None" = None,
) -> tuple[str, str]:
    """Genera el preámbulo LaTeX dividido en importaciones y configuración.

    Para cada lenguaje con LanguageColorConfig:
      - Genera \\lstdefinelanguage desde las reglas del config (keywords, comentarios,
        strings) → listings sabe exactamente qué tokens colorear.
      - Genera \\lstdefinestyle con morekeywords + colores → listings sabe CON QUÉ
        color hacerlo.
    Para lenguajes sin config, usa las definiciones hardcodeadas de _CUSTOM.

    Args:
        languages: Conjunto de nombres de lenguaje tal como aparecen en el MD.
        color_configs: dict {lang_lower: LanguageColorConfig} opcional.

    Returns:
        Tupla (imports_block, config_block).
    """
    if not languages:
        return ("", "")

    imports = _IMPORTS
    config_parts = [_BASE_CONFIG]
    seen_lang_defs: set[str] = set()

    for lang in sorted(languages):
        key = lang.lower().strip()
        key = _CUSTOM_ALIASES.get(key, key)
        cfg = (color_configs or {}).get(key)

        # ── Definición del lenguaje ────────────────────────────────────
        if key not in seen_lang_defs:
            if cfg and (cfg.keywords_list or cfg.comment_line or cfg.string_delimiters):
                # El config tiene reglas sintácticas → generamos desde él
                # (reemplaza la definición hardcodeada de _CUSTOM)
                config_parts.append(_generate_lstdefinelanguage(cfg, key))
            elif key in _CUSTOM:
                # Sin config o config sin reglas → usar la definición hardcodeada
                config_parts.append(_CUSTOM[key])
            # Para lenguajes nativos (_NATIVE) no se añade \lstdefinelanguage
            seen_lang_defs.add(key)

        # ── Estilo de color ────────────────────────────────────────────
        if cfg:
            # cfg.to_latex() ya incluye morekeywords + keywordstyle por grupos
            config_parts.append(cfg.to_latex())

    return (imports, "\n".join(config_parts))
