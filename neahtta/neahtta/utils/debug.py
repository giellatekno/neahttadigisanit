import os.path
import os
# import traceback

level = 0
cwd = os.getcwd()  # /home/anders/projects/neahttadigisanit/neahtta

IGNORE_FILES = ["trie.py"]

# The functions we want to trace
TRACE_FUNCTIONS = set()


# def TRACE():
#     frame = next(iter(traceback.walk_stack(None)))[0]
#     fname = frame.f_code.co_name
#     if fname not in TRACE_FUNCTIONS:
#         TRACE_FUNCTIONS.add(frame.f_code.co_name)
#         # calling this manually here doesn't properly register, so we
#         # won't get the return value captured on the first invocation
#         frame.f_trace = tracefn
#         tracefn(frame, "call", None)
#         #call(frame)


def DEBUG(s):
    print("  " * level + s)


def func_is_internal(filename, file):
    relpath = os.path.relpath(file)
    if (
        relpath.startswith("<frozen")
        or relpath.startswith("<string>")
        or relpath.startswith("<module>")
    ):
        return True

    path_is_venv = relpath.startswith("venv")
    if path_is_venv:
        # print("path_is_venv", filename, file)
        return True

    common_path = os.path.commonpath((cwd, os.path.abspath(file)))
    if common_path != cwd:
        # print("common_path is not cwd", filename, file)
        return True


def _tracing_handle_value(v):
    if isinstance(v, bytes):
        v = f"<bytes ({str(v[0:10])}...)>"
    elif isinstance(v, dict):
        # a bit too verbose..
        # v = "{" + ", ".join(f"{k}: {V}" for k, V in v.items()) + "}"
        v = "<dict>"
    elif isinstance(v, (tuple, list)):
        start_bracket = "[" if isinstance(v, list) else "("
        els = [_tracing_handle_value(el) for el in v[0:5]]
        ret = start_bracket + ", ".join(els)
        if len(v) > 5:
            ret += f", <...and {len(v) - 5} more elements...>"
        ret += "]" if isinstance(v, list) else ")"
        v = ret
    elif isinstance(v, str):
        if len(v) > 40:
            x = v[0:40].replace("\n", "\\n")
            v = f'"{x} <...more>"'
        else:
            x = v.replace("\n", "\\n")
            v = f'"{x}"'
    else:
        v = str(v).replace("\n", "\\n")
        if len(v) > 40:
            v = v[0:40] + " <...more>"
    return v


def _call(frame):
    global level

    filename = frame.f_code.co_filename
    file = os.path.relpath(filename, cwd)

    if file == "":
        pass
    elif file.startswith(".."):
        # not part of our code
        pass
    elif file.startswith("<frozen"):
        # some built in thing
        pass
    elif file.startswith("venv"):
        # venv check
        pass
    elif file.startswith("<builder:") or file.startswith("<werkzeug"):
        # werkzeug thing
        pass
    elif file == "<string>":
        # when does this happen, exactly?
        pass
    elif file.startswith("<template>"):
        # code running in a template
        pass
    elif file.startswith("neahtta/templates"):
        # ignoring any code in this path
        pass
    elif file.endswith("context_processors.py"):
        pass
    else:
        qualname = frame.f_code.co_qualname
        if qualname == "_tracing_handle_value":
            return
        elif qualname.startswith("Tagsets"):
            return
        elif "tagfilter" in qualname:
            return
        elif qualname.startswith("TagPart"):
            # don't want to see any of the TagPart things (__iter__, __hash__)
            return
        elif qualname.endswith("iso_has_flag"):
            return
        elif qualname.endswith("<listcomp>"):
            return
        elif qualname.startswith("splitTagByCompound"):
            return
        elif qualname.startswith("register_babel"):
            return
        elif qualname.startswith("root"):
            return
        elif qualname.startswith("hash_node"):
            return
        elif qualname.startswith("iso_filter"):
            return
        elif qualname.startswith("urlencode_filter_quote"):
            return
        elif qualname.startswith("register_template_filters.<locals>"):
            return
        elif qualname.startswith("Tag."):
            return
        elif qualname.endswith("iso_to_language_own_name"):
            return
        elif qualname.endswith("append_language_names_i18n"):
            return
        elif qualname == "DEBUG":
            return
        args = repr_args(frame)
        print("  " * level + f"{file}:{qualname}({args})")
        level += 1
        return tracefn


def _return(frame, arg):
    global level
    level -= 1
    retval = _tracing_handle_value(arg)
    func_name = frame.f_code.co_name
    print("  " * level + f"{func_name}() ->", retval)
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


def tracefn(frame, event, arg):
    if event == "call":
        return _call(frame)
    elif event == "return":
        return _return(frame, arg)
    elif event == "line":
        pass
    elif event == "exception":
        pass
    elif event == "opcode":
        pass


# OLD

# import os.path
# import os
# import traceback
#
# level = 0
# cwd = os.getcwd()  # /home/anders/projects/neahttadigisanit/neahtta
#
# IGNORE_FILES = ["trie.py"]
#
# # The functions we want to trace
# TRACE_FUNCTIONS = set()
#
#
# def TRACE():
#     frame = next(iter(traceback.walk_stack(None)))[0]
#     fname = frame.f_code.co_name
#     if fname not in TRACE_FUNCTIONS:
#         TRACE_FUNCTIONS.add(frame.f_code.co_name)
#         # calling this manually here doesn't properly register, so we
#         # won't get the return value captured on the first invocation
#         frame.f_trace = tracefn
#         #tracefn(frame, "call", None)
#         call(frame)
#
#
# def DEBUG(s):
#     print("  " * level, s)
#
#
# def func_is_internal(filename, file):
#     relpath = os.path.relpath(file)
#     if (
#         relpath.startswith("<frozen")
#         or relpath.startswith("<string>")
#         or relpath.startswith("<module>")
#     ):
#         return True
#
#     path_is_venv = relpath.startswith("venv")
#     if path_is_venv:
#         # print("path_is_venv", filename, file)
#         return True
#
#     common_path = os.path.commonpath((cwd, os.path.abspath(file)))
#     if common_path != cwd:
#         # print("common_path is not cwd", filename, file)
#         return True
#
#
# def handle_value(v):
#     if isinstance(v, bytes):
#         v = f"<bytes ({str(v[0:10])}...)>"
#     elif isinstance(v, dict):
#         v = "<dict>"
#     elif isinstance(v, (tuple, list)):
#         start_bracket = "[" if isinstance(v, list) else "("
#         els = [handle_value(el) for el in v[0:5]]
#         ret = start_bracket + ", ".join(els)
#         if len(v) > 5:
#             ret += f", <...and {len(v) - 5} more elements...>"
#         ret += "]" if isinstance(v, list) else ")"
#         v = ret
#     elif isinstance(v, str):
#         if len(v) > 40:
#             x = v[0:40].replace("\n", "\\n")
#             v = f'"{x} <...more>"'
#         else:
#             x = v.replace("\n", "\\n")
#             v = f'"{x}"'
#     else:
#         v = str(v).replace("\n", "\\n")
#         if len(v) > 40:
#             v = v[0:40] + " <...more>"
#     return v
#
#
# def call(frame):
#     func_name = frame.f_code.co_name
#     print("DEBUG", func_name)
#     return lambda *_: None
#
#
# def tracefn(frame, event, arg):
#     global level
#     if event == "call":
#         # doesn't exist in 3.9
#         # qualname = frame.f_code.co_qualname
#         # print(qualname)
#         func_name = frame.f_code.co_name
#         if func_name not in TRACE_FUNCTIONS:
#             return
#         if func_name.startswith("<module>"):
#             print("tracer: ignoring func_name<module>")
#             return
#
#         filename = frame.f_code.co_filename
#         file = os.path.relpath(filename, cwd)
#         if func_is_internal(filename, file):
#             return
#
#         if not filename:
#             print("tracer: ignoring when no filename")
#             return
#
#         if os.path.basename(filename) in IGNORE_FILES:
#             print("tracer: ignored file", filename)
#             return
#
#         n_pos_args = frame.f_code.co_argcount
#         n_kw_args = frame.f_code.co_kwonlyargcount
#         n_args = n_pos_args + n_kw_args
#
#         varnames = frame.f_code.co_varnames
#         param_names = varnames[0:n_args]
#         args = []
#         for param_name in param_names:
#             param_value = frame.f_locals[param_name]
#             args.append((param_name, param_value))
#
#         param_strings = []
#         try:
#             for k, v in args:
#                 # We assume nobody has an argument called "self" to a plain
#                 # function, and that "self" is always the actual self of an
#                 # object
#                 if k == "self":
#                     continue
#                 v = handle_value(v)
#                 param_strings.append(f"{k}={v}")
#             param_string = ", ".join(param_strings)
#         except AttributeError:
#             # something happened here, just ignore tracing
#             pass
#         else:
#             print("  " * level, end="")
#             print(f"{file} :: {func_name}({param_string})")
#             level += 1
#             return tracefn
#     elif event == "return":
#         level -= 1
#         retval = handle_value(arg)
#         func_name = frame.f_code.co_name
#         print("  " * level + f"{func_name}() ->", retval)
#         return tracefn
#     elif event == "line":
#         pass
#     elif event == "exception":
#         pass
#     elif event == "opcode":
#         pass
