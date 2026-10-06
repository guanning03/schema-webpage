# Schema paper website

Project page for **Schema: Discovering Unknown Environments via Agentic Program
Induction**.

- Website: <https://guanning03.github.io/schema-webpage/>
- Repository: <https://github.com/guanning03/schema-webpage>

## Publishing

GitHub Pages publishes the root of the `main` branch. Push changes to `main`
to update the website. `.nojekyll` keeps the site as plain static HTML.
All asset URLs are relative so the page works under `/schema-webpage/`.

The site includes all 25 ARC-AGI-3 runs, all 21 DiG-bench videos, the MazeBench
replay, and four complete-level case comparisons. Case GIFs and posters are
rendered at 3x density (2376 × 1278) for clear text on Retina screens. The page
plays equivalent silent MP4 loops so pausing or scrolling away preserves the
current frame. Every action and key-frame pause is retained; the shorter run
holds its completed state until the longer run finishes.

## Local preview

```sh
python3 serve.py --port 8080
```

Open <http://localhost:8080>. The local server supports video byte ranges.
No installation or build step is required. On macOS, `start-preview.command`
also launches the local preview.

## Source and assets

- `index.html`: paper overview, method, results, case studies, videos, citation.
- `static/`: template styles, local fonts, logos, and page interactions.
- `assets/`: paper PDF, figures, videos, posters, and case comparisons.
- `assets/cases/full_level_manifest.json`: recorded runs, action indices, grid
  hashes, and timing used to render the complete-level comparisons.
- `scripts/`: reproducible figure and media preparation scripts. Regenerating
  media requires the original research files in the parent workspace, plus
  the dependencies specified in each script. They are not needed for hosting.
- `scripts/prepare_case_replays.py`: converts the source GIFs to browser replays,
  verifying every frame timestamp and duration, with first-frame posters.

## Attribution

Adapted from the [MaxRL website source](https://github.com/Zanette-Labs/MaxRL/tree/master/site)
at commit `8bafaa9cf04c9d68511afd4c2cff75afbc8dc3a2`, retaining its layout and base
styles, with Schema paper content and media.

Website template: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
with attribution to [MaxRL](https://zanette-labs.github.io/MaxRL/) and
[Nerfies](https://github.com/nerfies/nerfies.github.io).
Paper and research assets retain their own applicable rights.
