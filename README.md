# Kotoba Meteor — standalone game

A static Japanese vocabulary game, independent from the NHK Easy Reader. No npm installation, server-side runtime, secrets, or build step required.

## Local preview

Run from this directory:

```bash
python3 -m http.server 8000
```

Open http://localhost:8000. Opening `index.html` directly as a file is not supported because the game fetches `meteor-lexicon.json` over HTTP.

## Deploy to Cloudflare Pages with GitHub

1. Create a **new GitHub repository** named `kotoba-meteor` (separate from the NHK Reader).
2. Upload the **contents of this folder** to the repository root: `index.html`, `meteor-lexicon.json`, `image-manifest.json`, `build_meteor_lexicon.py`, and `README.md`. Do not upload the enclosing folder as an extra level.
3. In the Cloudflare dashboard, go to **Workers & Pages → Create → Pages → Connect to Git** (wording may vary), authorize GitHub, and select the new repository.
4. Choose **no framework / None**. Leave the **build command blank**. Set the **build output directory** to `.` (repository root). If the dashboard requires a build command, use `exit 0`.
5. Deploy. Cloudflare will provide a `*.pages.dev` URL. New commits to the connected branch trigger redeployments.

If your Cloudflare dashboard only offers a Workers Git integration, choose the **Pages** creation flow rather than a Worker; do not deploy the NHK Reader Worker to this project.

## Vocabulary and images

- `meteor-lexicon.json`: 18,000 JMdict entries, fetched by the browser at startup to supply distractors.
- The initial game bank is 60 starter words. Word bank edits are stored in that browser's `localStorage` and **are not shared across users or devices**. Export your word bank JSON to keep a backup.
- `image-manifest.json`: empty placeholder for a future image dictionary; the current game does not load it.
- To regenerate the dictionary, run `python3 build_meteor_lexicon.py /path/to/JMdict_e.gz` from this folder and commit the updated JSON.
- Pronunciation uses the browser's Japanese speech synthesis voices; results vary by device.

## Licensing

JMdict data © Electronic Dictionary Research and Development Group, CC BY-SA 4.0. See https://www.edrdg.org/edrdg/licence.html . Review attribution/share-alike obligations when redistributing modified dictionary data.

## Scope

This repository is a standalone copy. No NHK Reader files or Cloudflare Worker endpoints are required. Future image and dictionary management can be added without changing the Reader.
