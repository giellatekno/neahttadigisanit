#!/usr/bin/env python3

# /// script
# dependencies = [
#     "ruamel.yaml"
# ]
# ///

"""
Change the start_query setting to gtweb-02.uit.no in the config files,
for when gtweb-02 (where korp is hosted) takes over for the old gtweb server.
"""

import argparse
import re
from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML()
PAT = re.compile(r"^(?P<whitespace>\s*)start_query: '.*'$")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, nargs="+")
    return parser.parse_args()


def main():
    args = parse_args()

    for file in args.file:
        print(f"processing {file}...")
        lang = file.name[0:3]
        config_text = file.read_text()
        config_doc = yaml.load(file)

        try:
            dictionary_config_iter = iter(config_doc["Dictionaries"])
        except KeyError:
            # this config has no "Dictionaries:"
            continue

        lines = []

        # save a backup file, with the same name as the original file, just
        # with an ".orig"-suffix
        orig_file = file.with_suffix(f"{file.suffix}.orig")
        orig_file.write_text(config_text)

        # We go line by line in the original config, and if the line is not
        # the config line we want to change, we just copy it back out.
        # When we find the line we are after, we advance the the yaml parser
        # to the corresponding dictionary configuration block, so that we
        # can retreive the language for that link. The new korp url structure
        # is divided into one korp per language.
        for line in config_text.split("\n"):
            m = re.match(PAT, line)
            if m is None:
                lines.append(line)
            else:
                # we found the line, but in order to know which language
                # it should be, we need to load the corresponding dictioanry
                # block from the configuration

                # So, we need to skip dictionary entries that do not have
                # a "start_query" key, to not get out of sync
                while True:
                    dict_settings = next(dictionary_config_iter)
                    if "start_query" in dict_settings:
                        break

                # now, the lang is usually in the "source", but sometimes,
                # instead of an actual language tag, it will say "SoMe"
                # ("Social Media"), indicating support for "easier typing",
                # e.g. the ability for the user to use letters that are easier
                # to type on a keyboard (the users may not have the keys),
                # e.g. "c" instead of "č", etc.
                # ---- anyway ----
                # we have to read lang from the "path" property, which is
                # always in the format 'dicts/AAA-BBB.xml' (where AAA and BBB
                # are language codes)
                lang = dict_settings["path"][6:9]
                indent = m.group("whitespace")
                new_url = f"https://gtweb-02.uit.no/korp/{lang}?"
                updated_line = f"{indent}start_query: '{new_url}'"
                lines.append(updated_line)

        new_text = "\n".join(lines)
        file.write_text(new_text)


if __name__ == "__main__":
    raise SystemExit(main())
