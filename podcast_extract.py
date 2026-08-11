#!/usr/bin/env python3
"""Extract episode URLs and chapters from a Podlove-chaptered podcast RSS feed."""
import argparse
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

NS = {"psc": "http://podlove.org/simple-chapters"}


NS_ITUNES = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}


def parse(path):
    # feed declares itunesu: prefix without an xmlns; patch it in so ET can parse.
    if path.startswith(("http://", "https://")):
        req = urllib.request.Request(path, headers={"User-Agent": "AntennaPod/4.2.3"})
        with urllib.request.urlopen(req) as r:
            text = r.read().decode("utf-8")
    else:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    if "xmlns:itunesu=" not in text:
        text = text.replace("<rss ", '<rss xmlns:itunesu="http://www.itunesu.com/feed/1.0" ', 1)
    root = ET.fromstring(text)
    channel = root.find("channel")
    artist = (channel.findtext("itunes:author", namespaces=NS_ITUNES) or "").strip() or None
    album = (channel.findtext("title") or "").strip() or None
    episodes = []
    for item in root.iter("item"):
        enclosure = item.find("enclosure")
        chapters = [
            {"start": c.get("start"), "title": c.get("title")}
            for c in item.findall("psc:chapters/psc:chapter", NS)
        ]
        episodes.append({
            "title": (item.findtext("title") or "").strip(),
            "url": enclosure.get("url") if enclosure is not None else None,
            "guid": (item.findtext("guid") or "").strip() or None,
            "artist": artist,
            "album": album,
            "chapters": chapters,
        })
    return episodes


def demo():
    import tempfile, os
    sample = """<rss><channel><item>
      <title>t</title>
      <enclosure url="http://x/a.opus"/>
      <guid>g1</guid>
      <psc:chapters xmlns:psc="http://podlove.org/simple-chapters">
        <psc:chapter start="00:00:00.000" title="one"/>
      </psc:chapters>
    </item></channel></rss>"""
    fd, p = tempfile.mkstemp(suffix=".xml")
    os.write(fd, sample.encode())
    os.close(fd)
    try:
        eps = parse(p)
        assert len(eps) == 1
        assert eps[0]["url"] == "http://x/a.opus"
        assert eps[0]["chapters"] == [{"start": "00:00:00.000", "title": "one"}]
    finally:
        os.remove(p)
    print("demo ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("feed", nargs="?", help="local path or URL to podcast.xml")
    ap.add_argument("-v", "--verbose", action="store_true", help="print episode/chapter counts to stderr")
    ap.add_argument("--demo", action="store_true", help="run self-check and exit")
    args = ap.parse_args()

    if args.demo:
        demo()
    elif not args.feed:
        ap.error("feed is required (or pass --demo)")
    else:
        episodes = parse(args.feed)
        if args.verbose:
            print(f"{len(episodes)} episodes, {sum(len(e['chapters']) for e in episodes)} chapters",
                  file=sys.stderr)
        print(json.dumps(episodes, indent=2, ensure_ascii=False))
