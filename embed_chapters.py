#!/usr/bin/env python3
# /// script
# dependencies = ["mutagen"]
# ///
"""Download episodes from a podcast RSS feed and embed their Podlove chapters
as Ogg Vorbis-comment CHAPTERxxx/CHAPTERxxxNAME tags (read by ffmpeg/mpv/VLC/foobar2000).
"""
import argparse
import os
import subprocess
from mutagen.oggopus import OggOpus

from podcast_extract import parse

DEFAULT_RATE = "1m"  # wget --limit-rate; be polite to the server


def chapter_tags(chapters):
    tags = {}
    for i, ch in enumerate(chapters, start=1):
        n = f"{i:03d}"
        tags[f"CHAPTER{n}"] = [ch["start"]]
        tags[f"CHAPTER{n}NAME"] = [ch["title"]]
    return tags


def download(url, outdir, rate, verbose=False):
    # -c resumes partial files; -N (timestamping) skips up-to-date files and
    # re-fetches ones the server has updated. Needs wget to name the file
    # itself (-P dir) since -N doesn't work together with -O.
    subprocess.run(
        ["wget", "-nv" if not verbose else "-v", "-c", "-N", "--limit-rate", rate,
         "--user-agent", "AntennaPod/4.2.3", "-P", outdir, url],
        check=True,
    )


def embed(path, ep):
    f = OggOpus(path)
    for k in [k for k in f.keys() if k.upper().startswith("CHAPTER")]:
        del f[k]
    tags = chapter_tags(ep["chapters"])
    tags["TITLE"] = [ep["title"]]
    if ep.get("artist"):
        tags["ARTIST"] = [ep["artist"]]
    if ep.get("album"):
        tags["ALBUM"] = [ep["album"]]
    f.update(tags)
    f.save()


def run(feed_path, outdir, match=None, rate=DEFAULT_RATE, artist=None, verbose=False):
    os.makedirs(outdir, exist_ok=True)
    episodes = parse(feed_path)
    if match:
        episodes = [e for e in episodes if match.lower() in e["title"].lower()]
    if artist:
        for e in episodes:
            e["artist"] = artist
    for ep in episodes:
        if not ep["url"] or not ep["chapters"]:
            continue
        dest = os.path.join(outdir, os.path.basename(ep["url"]))
        download(ep["url"], outdir, rate, verbose)
        embed(dest, ep)
        print(f"embedded {len(ep['chapters'])} chapters -> {dest}")


def demo():
    import tempfile, shutil, subprocess
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(tmp, "a.opus")
        # generate a tiny real opus file with ffmpeg so mutagen can tag it
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=8000:cl=mono",
             "-t", "0.2", "-c:a", "libopus", src],
            check=True, capture_output=True,
        )
        embed(src, {
            "title": "ep title",
            "artist": "the artist",
            "album": "the show",
            "chapters": [{"start": "00:00:00.000", "title": "one"}],
        })
        f = OggOpus(src)
        assert f["CHAPTER001"] == ["00:00:00.000"]
        assert f["CHAPTER001NAME"] == ["one"]
        assert f["ARTIST"] == ["the artist"]
        assert f["ALBUM"] == ["the show"]
    finally:
        shutil.rmtree(tmp)
    print("demo ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("feed", nargs="?", help="local path or URL to podcast.xml")
    ap.add_argument("outdir", nargs="?", default="episodes", help="download directory (default: episodes)")
    ap.add_argument("--match", help="only episodes whose title contains this substring")
    ap.add_argument("--rate", default=DEFAULT_RATE, help="wget --limit-rate (default: %(default)s)")
    ap.add_argument("--artist", help="override the ARTIST tag (default: feed's itunes:author)")
    ap.add_argument("-v", "--verbose", action="store_true", help="show wget's normal progress output")
    ap.add_argument("--demo", action="store_true", help="run self-check and exit")
    args = ap.parse_args()

    if args.demo:
        demo()
    elif not args.feed:
        ap.error("feed is required (or pass --demo)")
    else:
        run(args.feed, args.outdir, args.match, args.rate, args.artist, args.verbose)
