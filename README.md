# podcast-chapters

Extract episode URLs/chapters from a Podlove-chaptered podcast RSS feed, and
optionally embed those chapters into the downloaded Opus files.

## Requirements

- `wget`
- the `mutagen` Python package - on Debian 13: `sudo apt install python3-mutagen`

## Usage

```
# feed can be a local path or a URL
uv run podcast_extract.py podcast.xml            # dump episodes+chapters as JSON

uv run embed_chapters.py podcast.xml [outdir] [--match SUBSTR] [--rate 1m]
```

`embed_chapters.py` downloads each episode with `wget` (rate-limited,
resumable, skips up-to-date files, re-fetches ones the server updated) and
writes `CHAPTERxxx`/`CHAPTERxxxNAME` + `TITLE`/`ARTIST`/`ALBUM` Vorbis
comments into the local file with `mutagen`. Chapters embedded this way are
read natively by ffmpeg, mpv, VLC, and foobar2000 - no separate playlist file
needed.

Run `uv run <script>.py --demo` for a quick self-check.
