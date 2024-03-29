""" Audio export thing.

A commandline tool to extract audio files, and replace the paths in
the lexicon with the updated paths.

Usage: tools/extract_audio.py [options] <source_lexicon> <path_to_audio> 

Options:
    -h --help                  Show this screen.
    -v --verbose               Verbose.
    -e --encoding-format=FMT   Encoding format. [default: m4a]
    -l --local-audio-source    Use local file source, do not download [default: false]
    -o --output-file=PATH      Destination file for edited XML
"""

# TODO: option for no fetch, incase they are stored locally: <path_to_audio> is
# the target compressed audio store for now, but could serve as local copy too
#
# python tools/extract_audio.py dicts/sms-all.xml static/aud/sms --verbose > test_aud.xml

import os
import sys

import requests
from lxml import etree

# TODO: only download updated files, storing in manifest in path/to/stored/audio/
from docopt import docopt


# [(Url, Target)] -> [(Url, TranscodedTarget)]
def transcode_audios(audio_paths, fmt="m4a", verbose=False):
    import subprocess

    def proc(*args):
        PIPE = subprocess.PIPE
        if verbose:
            print(args, file=sys.stderr)
        try:
            p = subprocess.call(" ".join(args), shell=True, stdout=PIPE, stderr=PIPE)
        except OSError:
            sys.exit("Problem transcoding. Is ffmpeg installed?")
        if verbose:
            print(p, file=sys.stderr)
            print(p.stdout, file=sys.stderr)

    transcoded_paths = []

    for url, target in audio_paths:
        transcoded_target = target.replace(".wav", "." + fmt)
        if os.path.exists(transcoded_target):
            print(" * already converted: <%s>" % transcoded_target, file=sys.stderr)
        else:
            proc("ffmpeg", "-i", target, transcoded_target)
            print(" * converted: <%s>" % transcoded_target, file=sys.stderr)
        transcoded_paths.append((url, transcoded_target))

    return transcoded_paths


# url -> basename
def filename_from_url(url):
    from urlparse import urlparse
    import ntpath

    o = urlparse(url)
    path = o.path
    base = ntpath.basename(path)
    # filename
    return base


# file path -> file path; include environment variables
def file_path_with_env(_path):
    import os

    return os.path.expandvars(_path)


#  -> (path, local_target, modified)
def copy_file(path, target_dir, cache=True, verbose=False):
    import ntpath
    from shutil import copy

    if verbose:
        print(" * copying <%s> " % filename_from_url(url), file=sys.stderr)

    source_path = file_path_with_env(path)
    filename = ntpath.basename(source_path)

    local_target = os.path.join(target_dir, filename)
    target_dir = os.path.join(target_dir)

    copy(source_path, target_dir)

    return (path, local_target, True)


def fetch(url, target_dir, cache=True, verbose=False):
    if verbose:
        print(" * fetching <%s> " % filename_from_url(url), file=sys.stderr)
    filename = filename_from_url(url)
    local_target = os.path.join(target_dir, filename)

    if cache:
        # TODO: check that the data stored, when cached, is correct
        try:
            exists = open(local_target, "r")
            exists.close()
            print(" * already stored <%s>" % local_target, file=sys.stderr)
            # TODO: modified?
            return (url, local_target, False)
        except:
            pass

    r = requests.get(url, stream=True)
    if not r.ok:
        what

    with open(local_target, "w") as F:
        print(" * Downloading <%s> " % local_target, file=sys.stderr)
        for block in r.iter_content(1024):
            F.write(block)
        print(" * Done.", file=sys.stderr)

    modified = r.headers.get("last-modified", False)
    return (url, local_target, modified)


def read_audio_dates(audio_target):
    # TODO:
    # [(target_uri, source_modified)
    return False


def cache_dates(downloaded_audios, audio_target):
    # TODO: store to audio_target/source_last_updated.txt
    # which is formatted:
    #   target_url\tfilename\tdate
    #   target_url\tfilename\tdate
    return False


# [source,]
def copy_audios(audio_paths, audio_target, verbose=False):
    # TODO: check for source_last_updated.txt
    # TODO: filter audio_urls by those that really need an update --
    #    remote header is newer than stored header

    copied_audios = []
    file_updates = []

    for aud in audio_paths:
        _, file_path, source_modified = copy_file(aud, audio_target, verbose=verbose)
        copied_audios.append((aud, file_path))
        file_updates.append((aud, file_path, source_modified))

    # TODO: cache_dates(file_updates, audio_target)
    #  - but only the ones with a date provided.

    # [(source, target), ... ]
    return copied_audios


# [source,]
def download_audios(audio_urls, audio_target, verbose=False):
    # TODO: check for source_last_updated.txt
    # TODO: filter audio_urls by those that really need an update --
    #    remote header is newer than stored header

    downloaded_audio = []
    file_updates = []

    for aud in audio_urls:
        _, file_path, source_modified = fetch(aud, audio_target, verbose=verbose)
        downloaded_audio.append((aud, file_path))
        file_updates.append((aud, file_path, source_modified))

    # TODO: cache_dates(file_updates, audio_target)
    #  - but only the ones with a date provided.

    # [(source, target), ... ]
    return downloaded_audio


# lxml_root, [(source, target), ... ]
def replace_audio_paths(xml_root, stored_audio):
    import copy

    root_duplicate = copy.deepcopy(xml_root)

    nodes_with_files = etree.XPath(
        ".//e[lg/audio/a/@href]",
    )(root_duplicate)

    stored_audios = dict(stored_audio)

    def format_path(path):
        # TODO: adjust formatting so that it is relative to the server.
        return path

    # nodes with audios get replaced with the new URL.
    for node in nodes_with_files:
        auds = node.xpath(".//lg/audio/a")
        for a in auds:
            oldpath = a.attrib["href"]
            newpath = stored_audios.get(oldpath, False)
            if newpath:
                a.attrib["href"] = "/" + newpath

    # new xml root
    return root_duplicate


def write_xml(root, output_file=False):
    # TODO: strips some headers
    stringed = etree.tostring(root, pretty_print=True, method="xml", encoding="unicode")

    if output_file is not None:
        with open(output_file, "w") as F:
            F.write(stringed.encode("utf-8"))
    else:
        print(stringed.encode("utf-8"), file=sys.stdout)


def main():
    arguments = docopt(__doc__, version="asdf")

    infile = arguments.get("<source_lexicon>")
    audio_target = arguments.get("<path_to_audio>")
    verbose = arguments.get("--verbose")
    encoding_format = arguments.get("--encoding-format", "m4a")

    root = etree.parse(infile)

    files = etree.XPath(
        ".//e/lg/audio/a/@href",
    )
    urls = files(root)

    local = arguments.get("--local-audio-source", False)

    if local:
        stored_audio = copy_audios(urls, audio_target)
    else:
        stored_audio = download_audios(urls, audio_target)

    transcoded_audio = transcode_audios(stored_audio, fmt=encoding_format)

    updated_xml = replace_audio_paths(root, transcoded_audio)
    write_xml(updated_xml, arguments.get("--output-file"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
