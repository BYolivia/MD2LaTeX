"""
Soporte de lenguajes para el entorno lstlisting de LaTeX.

Distingue entre lenguajes nativos del paquete listings y lenguajes que
necesitan una definición personalizada (lstdefinelanguage).
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Lenguajes soportados de forma nativa por el paquete listings
# Clave: nombre normalizado (lowercase sin puntuación especial)
# Valor: nombre exacto que acepta listings (sensible a mayúsculas)
# ---------------------------------------------------------------------------
_NATIVE: dict[str, str] = {
    # Shells / scripting
    "bash": "bash",
    "sh": "sh",
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
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
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
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
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
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
  morestring=[b]',
  morestring=[b]",
  morestring=[b]`,
  sensitive=true,
}""",

    "rust": r"""
\lstdefinelanguage{Rust}{
  keywords={as,async,await,break,const,continue,crate,dyn,else,enum,extern,
    false,fn,for,if,impl,in,let,loop,match,mod,move,mut,pub,ref,return,
    self,Self,static,struct,super,trait,true,type,unsafe,use,where,while,
    abstract,become,box,do,final,macro,override,priv,try,typeof,unsized,
    virtual,yield,i8,i16,i32,i64,i128,isize,u8,u16,u32,u64,u128,usize,
    f32,f64,bool,char,str,String,Vec,Option,Result,Some,None,Ok,Err},
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
  morestring=[b]',
  morestring=[b]",
  sensitive=true,
}""",

    "kotlin": (
        r"\lstdefinelanguage{Kotlin}{" "\n"
        r"  keywords={abstract,actual,annotation,as,break,by,catch,class,companion," "\n"
        r"    const,constructor,continue,crossinline,data,delegate,do,dynamic,else," "\n"
        r"    enum,expect,external,false,field,file,final,finally,for,fun,get,if," "\n"
        r"    import,in,infix,init,inline,inner,interface,internal,is,it,lateinit," "\n"
        r"    noinline,null,object,open,operator,out,override,package,param,private," "\n"
        r"    property,protected,public,receiver,reified,return,sealed,set,setparam," "\n"
        r"    super,suspend,tailrec,this,throw,true,try,typealias,typeof,val,value," "\n"
        r"    var,vararg,when,where,while}," "\n"
        r"  keywordstyle=\color{blue}\bfseries," "\n"
        r"  comment=[l]{//}," "\n"
        r"  morecomment=[s]{/*}{*/}," "\n"
        r"  commentstyle=\color{gray}\itshape," "\n"
        r"  stringstyle=\color{red!70!black}," "\n"
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
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
  morestring=[b]',
  morestring=[b]",
  sensitive=true,
}""",

    "json": r"""
\lstdefinelanguage{JSON}{
  morestring=[b]",
  stringstyle=\color{red!70!black},
  literate=
    *{0}{{{\color{teal}0}}}{1}
     {1}{{{\color{teal}1}}}{1}
     {2}{{{\color{teal}2}}}{1}
     {3}{{{\color{teal}3}}}{1}
     {4}{{{\color{teal}4}}}{1}
     {5}{{{\color{teal}5}}}{1}
     {6}{{{\color{teal}6}}}{1}
     {7}{{{\color{teal}7}}}{1}
     {8}{{{\color{teal}8}}}{1}
     {9}{{{\color{teal}9}}}{1}
     {:}{{{\color{gray}{:}}}}{1}
     {,}{{{\color{gray}{,}}}}{1}
     {\{}{{{\color{blue}{\{}}}}{1}
     {\}}{{{\color{blue}{\}}}}}{1}
     {[}{{{\color{blue}{[}}}}{1}
     {]}{{{\color{blue}{]}}}}{1},
  sensitive=true,
}""",

    "yaml": r"""
\lstdefinelanguage{YAML}{
  keywords={true,false,null,yes,no,on,off},
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{\#},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
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
  keywordstyle=\color{blue},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
  morestring=[b]',
  morestring=[b]",
  sensitive=false,
}""",

    "dockerfile": r"""
\lstdefinelanguage{Dockerfile}{
  keywords={FROM,RUN,CMD,LABEL,EXPOSE,ENV,ADD,COPY,ENTRYPOINT,VOLUME,
    USER,WORKDIR,ARG,ONBUILD,STOPSIGNAL,HEALTHCHECK,SHELL,MAINTAINER,
    AS,to},
  keywordstyle=\color{blue}\bfseries,
  comment=[l]{\#},
  commentstyle=\color{gray}\itshape,
  stringstyle=\color{red!70!black},
  morestring=[b]',
  morestring=[b]",
  sensitive=true,
}""",

    "toml": (
        r"\lstdefinelanguage{TOML}{" "\n"
        r"  keywords={true,false,nan,inf}," "\n"
        r"  keywordstyle=\color{blue}\bfseries," "\n"
        r"  comment=[l]{\#}," "\n"
        r"  commentstyle=\color{gray}\itshape," "\n"
        r"  stringstyle=\color{red!70!black}," "\n"
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
        r"  keywordstyle=\color{blue}\bfseries," "\n"
        r"  comment=[l]{\#}," "\n"
        r"  commentstyle=\color{gray}\itshape," "\n"
        r"  stringstyle=\color{red!70!black}," "\n"
        r"  morestring=[b]'," "\n"
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


def build_preamble(
    languages: set[str],
    color_configs: "dict | None" = None,
) -> tuple[str, str]:
    """Genera el preámbulo LaTeX dividido en importaciones y configuración.

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
    seen_customs: set[str] = set()

    for lang in sorted(languages):
        key = lang.lower().strip()
        key = _CUSTOM_ALIASES.get(key, key)
        if key in _CUSTOM and key not in seen_customs:
            config_parts.append(_CUSTOM[key])
            seen_customs.add(key)

    # Añadir estilos de color si existen
    if color_configs:
        for lang in sorted(languages):
            key = lang.lower().strip()
            key = _CUSTOM_ALIASES.get(key, key)
            if key in color_configs:
                config_parts.append(color_configs[key].to_latex())

    return (imports, "\n".join(config_parts))
