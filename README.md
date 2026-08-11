# podcast-chapters

Extract episode URLs/chapters from a Podlove-chaptered podcast RSS feed, and
optionally embed those chapters into the downloaded Opus files.

## Usage

```
# feed can be a local path or a URL
python3 podcast_extract.py podcast.xml            # dump episodes+chapters as JSON

python3 embed_chapters.py podcast.xml [outdir] [--match SUBSTR] [--rate 1m]
```

`embed_chapters.py` downloads each episode with `wget` (rate-limited,
resumable, skips up-to-date files, re-fetches ones the server updated) and
writes `CHAPTERxxx`/`CHAPTERxxxNAME` + `TITLE`/`ARTIST`/`ALBUM` Vorbis
comments into the local file with `mutagen`. Chapters embedded this way are
read natively by ffmpeg, mpv, VLC, and foobar2000 - no separate playlist file
needed.

Requires `wget` and the `mutagen` Python package.

Run `python3 <script>.py --demo` for a quick self-check.
