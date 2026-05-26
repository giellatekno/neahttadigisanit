# beware: lots of globals in here...

import json
import os
import os.path

class TraceOpts:
    def __init__(self, opts: str | None = None):
        if isinstance(opts, str):
            options = opts.split(",")
            self.web = "web" in options

level = 0
cwd = os.getcwd()  # e.g. /home/anders/projects/neahttadigisanit/neahtta
traceopts = TraceOpts()


def tracefn(frame, event, arg):
    # we don't trace the other events ("line", "exception" and "opcode")
    if event == "call":
        return _call(frame)
    elif event == "return":
        return _return(frame, arg)


def set_trace_options(options):
    global traceopts
    traceopts = TraceOpts(options)


def _tracing_handle_bytes(v):
    if not traceopts.web:
        v = v[:10]
    return f"<bytes ({str(v)}...)>"


def _tracing_handle_seq(v):
    start_bracket = "[" if isinstance(v, list) else "("
    end_bracket = "]" if isinstance(v, list) else ")"

    n = len(v)
    if not traceopts.web:
        v = v[:5]
    els = [_tracing_handle_value(el) for el in v]
    s = ", ".join(els)
    if not traceopts.web and n > 5:
        s += f", <...and {len(v) - 5} more elements...>"

    return f"{start_bracket}{s}{end_bracket}"


def _tracing_handle_dict(v):
    if traceopts.web:
        return "{" + ", ".join(f"{k}: {V}" for k, V in v.items()) + "}"
    else:
        return "<dict>"


def _tracing_handle_str(v):
    v = v.replace("\n", "\\n")
    if len(v) <= 40 or traceopts.web:
        return f'"{v}"'
    else:
        v = v[:40]
        return f'"{v} <...more>"'


def _tracing_handle_other(v):
    v = str(v).replace("\n", "\\n")
    if len(v) > 40:
        v = v[0:40] + " <...more>"
    return v


def _tracing_handle_value(v):
    if isinstance(v, bytes):
        return _tracing_handle_bytes(v)
    elif isinstance(v, dict):
        return _tracing_handle_dict(v)
    elif isinstance(v, (tuple, list)):
        return _tracing_handle_seq(v)
    elif isinstance(v, str):
        return _tracing_handle_str(v)
    else:
        return _tracing_handle_other(v)
    return v


def ignore_file(file: str) -> bool:
    return (
        file == ""
        or
        # not part of our code
        file.startswith("..")
        or
        # some built in thing
        file.startswith("<frozen")
        or
        # venv check
        file.startswith("venv")
        or
        # werkzeug thing
        file.startswith("<builder:") or file.startswith("<werkzeug")
        or
        # when does this happen, exactly?
        file == "<string>"
        or
        # code running in a template
        file.startswith("<template>")
        or
        # ignoring any code in this path
        file.startswith("neahtta/templates")
        or
        file.endswith("context_processors.py")
        or
        file.endswith("config.py")
    )


def ignore_qualname(qualname: str) -> bool:
    return (
        qualname == "_tracing_handle_value"
        or
        qualname.startswith("Tagsets")
        or
        # don't want to see any of the TagPart things (__iter__, __hash__)
        "tagfilter" in qualname
        or
        qualname.startswith("TagPart")
        or
        qualname.endswith("iso_has_flag")
        or
        qualname.endswith("<listcomp>")
        or
        qualname.startswith("splitTagByCompound")
        or
        qualname.startswith("register_babel")
        or
        qualname.startswith("root")
        or
        qualname.startswith("hash_node")
        or
        qualname.startswith("iso_filter")
        or
        qualname.startswith("urlencode_filter_quote")
        or
        qualname.startswith("register_template_filters.<locals>")
        or
        qualname.startswith("Tag.")
        or
        qualname.endswith("iso_to_language_own_name")
        or
        qualname.endswith("append_language_names_i18n")
        or
        qualname == "DEBUG"
        or
        qualname.endswith("resolve_original_pair")
        or
        qualname.endswith("render_individual_template")
        or
        qualname.endswith("<genexpr>")
        or
        qualname.endswith("<lambda>")
        or
        qualname.endswith("get_template")
        or
        qualname.endswith("has_template")
        or
        qualname.endswith("template_name")
        or
        qualname.endswith("get_locale")
        or
        qualname.endswith("tag_processor")
        or
        qualname.endswith("LexRule.compare")
        or
        qualname.endswith("splitAnalysis")
        or
        qualname.endswith("evaluate")
        or
        qualname.endswith("compare")
        or
        qualname.endswith("xml_lang")
        or
        qualname.endswith("urlencode_filter_quote")
        or
        qualname.endswith("minority_langs_first")
    )


def _call(frame):
    global level

    filename = frame.f_code.co_filename
    file = os.path.relpath(filename, cwd)

    if ignore_file(file):
        return

    qualname = frame.f_code.co_qualname
    if ignore_qualname(qualname):
        return

    args = repr_args(frame)
    print("  " * level + f"{file}:{qualname}({args})")

    if traceopts.web:
        obj = {
            "type": "call",
            "level": level,
            "file": file,
            "qualname": qualname,
            "args": args,
        }

        with open(f"{cwd}/STRUCTURED_DEBUG_LOG", "a") as fp:
            json.dump(obj, fp)
            fp.write("\n")

    level += 1
    return tracefn


def _return(frame, arg):
    global level
    level -= 1
    retval = _tracing_handle_value(arg)
    func_name = frame.f_code.co_name
    print("  " * level + f"{func_name}() ->", retval)

    if traceopts.web:
        obj = {
            "type": "return",
            "level": level,
            "funcname": func_name,
            "retval": retval,
        }
        with open(f"{cwd}/STRUCTURED_DEBUG_LOG", "a") as fp:
            json.dump(obj, fp)
            fp.write("\n")

    return tracefn


def repr_args(frame):
    n_pos_args = frame.f_code.co_argcount
    n_kw_args = frame.f_code.co_kwonlyargcount
    n_args = n_pos_args + n_kw_args

    varnames = frame.f_code.co_varnames
    param_names = varnames[0:n_args]
    args = []
    for param_name in param_names:
        param_value = frame.f_locals[param_name]
        args.append((param_name, param_value))

    param_strings = []
    try:
        for k, v in args:
            # We assume nobody has an argument called "self" to a plain
            # function, and that "self" is always the actual self of an
            # object
            if k == "self":
                continue
            v = _tracing_handle_value(v)
            param_strings.append(f"{k}={v}")
        param_string = ", ".join(param_strings)
    except AttributeError:
        # something happened here, just ignore tracing
        pass

    return param_string
