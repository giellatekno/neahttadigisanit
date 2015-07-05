""" A commandline tool to extract audio files, and replace the paths in
the lexicon with the updated paths.

USAGE
    python tools/extract_audio.py source_lexicon.xml path/to/stored/audio/ > output_lexicon.xml

TODO: transcoding
TODO: only download updated files, storing in manifest in path/to/stored/audio/

"""

# find . \ -type file -name "*.mp3" | xargs -I {} ffmpeg -y -i {} -ab 96

# conversion type attr?

# for file in *.wav
#     do ffmpeg -i "${file}" "${file/%wav/m4a}"
# done

import os, sys
import requests

from lxml import etree

def transcode_audios(audio_paths, fmt="m4a"):
    import subprocess

    def proc(*args):
        PIPE = subprocess.PIPE
        print >> sys.stderr, args
        try:
            p = subprocess.call(args, shell=True)
        except OSError:
            sys.exit("Problem transcoding. Is ffmpeg installed?")
        print >> sys.stderr, p

    print >> sys.stderr, audio_paths

    transcoded_paths = []

    for url, target in audio_paths:
        transcoded_target = target.replace('.wav', '.m4a')
        proc("ffmpeg", "-i", target, transcoded_target)
        transcoded_paths.append((url, transcoded_target))


    print >> sys.stderr, "Transcoding complete."
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

def fetch(url, target_dir, cache=True):
    print >> sys.stderr, " * fetching <%s> " % url
    filename = filename_from_url(url)
    local_target = os.path.join(target_dir, filename)

    if cache:
        # TODO: check that the data stored, when cached, is correct
        try:
            exists = open(local_target, 'r')
            exists.close()
            print >> sys.stderr, " * already stored <%s>" % local_target
            # TODO: modified?
            return (url, local_target, False)
        except:
            pass

    r = requests.get(url, stream=True)
    if not r.ok:
        what

    with open(local_target, 'w') as F:
        print >> sys.stderr, " * writing to <%s> " % local_target
        for block in r.iter_content(1024):
            F.write(block)
        print >> sys.stderr, " * Done."

    modified = r.headers.get('last-modified', False)
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
def download_audios(audio_urls, audio_target):
    # TODO: check for source_last_updated.txt
    # TODO: filter audio_urls by those that really need an update -- 
    #    remote header is newer than stored header

    downloaded_audio = []
    file_updates = []

    for aud in audio_urls:
        _, file_path, source_modified = fetch(aud, audio_target)
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
        './/e[lg/audio/a/@href]',
    )(root_duplicate)

    stored_audios = dict(stored_audio)

    def format_path(path):
        # TODO: adjust formatting so that it is relative to the server.
        return path

    # nodes with audios get replaced with the new URL.
    for node in nodes_with_files:
        auds = node.xpath('.//lg/audio/a')
        for a in auds:
            oldpath = a.attrib['href']
            newpath  = stored_audios.get(oldpath, False)
            if newpath:
                a.attrib['href'] = newpath

    # new xml root
    return root_duplicate

def write_xml(root):
    # TODO: strips some headers
    stringed = etree.tostring(root, pretty_print=True, method='xml',
                              encoding='unicode')
    print >> sys.stdout, stringed.encode('utf-8')

def main():
    infile, audio_target = sys.argv[1::]

    root = etree.parse(infile)

    files = etree.XPath(
        './/e/lg/audio/a/@href',
    )
    urls = files(root)

    stored_audio = download_audios(urls, audio_target)
    transcoded_audio = transcode_audios(stored_audio)

    updated_xml = replace_audio_paths(root, transcoded_audio)
    write_xml(updated_xml)

if __name__ == "__main__":
    sys.exit(main())
