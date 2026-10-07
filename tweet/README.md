# Schema tweet preview

Published at https://guanning03.github.io/schema-webpage/tweet/.

This directory is independent of the main project page. All preview code, text, and media live under `tweet/`.

Edit `thread.json` for tweet text, attachment paths, or notes, then run:

```sh
python3 tweet/scripts/build_preview.py
```

The script uses only the Python standard library and writes `tweet/index.html`. Keep `thread.md` and the individual `posts/` copies in sync when editing the release copy. Media references are relative to this directory.

The preview is published as a draft; no posts have been sent to X.
