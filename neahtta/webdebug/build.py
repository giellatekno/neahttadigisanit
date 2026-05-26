#!/usr/bin/env python3

import json


def scriptsafe_str(s):
    return s.replace("</script>", "[[[ AN END OF SCRIPT HTML TAG HERE ]]]")


def main():
    with open("../STRUCTURED_DEBUG_LOG") as fp:
        log_lines = [json.loads(line) for line in fp]

    with open("template.html") as fp:
        template = fp.read()

    data = ",\n".join(scriptsafe_str(json.dumps(obj)) for obj in log_lines)
    index_html = template.replace("%%DATA%%", data)

    with open("index.html", "w") as fp:
        fp.write(index_html)


if __name__ == "__main__":
    raise SystemExit(main())
