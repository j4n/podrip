# podcast-chapters

Extract episode URLs/chapters from a Podlove-chaptered podcast RSS feed, and
optionally embed those chapters into the downloaded Opus files.

Two scripts, split by responsibility:

- **`podcast_extract.py`** - parses the feed into JSON. No downloads, no
  extra deps beyond the stdlib.
- **`embed_chapters.py`** - imports `parse()` from the above, then downloads
  each episode and writes the chapters into the file. Needs `wget` and
  `mutagen`.

## Requirements

- `wget`
- the `mutagen` Python package - `embed_chapters.py` carries a PEP 723 header
  so `uv run` installs it automatically; without uv, on Debian 13:
  `sudo apt install python3-mutagen`

## Usage

```
# <feed> is a local path or a URL
uv run podcast_extract.py <podcast.xml|feed URL> # dump episodes+chapters as JSON

uv run embed_chapters.py <podcast.xml|feed URL> [outdir] [--match SUBSTR] [--rate 1m] [--artist NAME]
```

`--artist` overrides the artist tag; by default it's taken from the feed's
`itunes:author`.

`embed_chapters.py` downloads each episode with `wget` (rate-limited,
resumable, skips up-to-date files, re-fetches ones the server updated) and
writes `CHAPTERxxx`/`CHAPTERxxxNAME` + `TITLE`/`ARTIST`/`ALBUM` Vorbis
comments into the local file with `mutagen`. Chapters embedded this way are
read natively by ffmpeg, mpv, VLC, and foobar2000 - no separate playlist file
needed.

Run `uv run <script>.py --demo` for a quick self-check.
