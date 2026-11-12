# padel-game.fun

Landing page, privacy policy, support and terms of use for the Padl iPhone app
(App Store name: Padel from Scratch), in 14 languages. Served by GitHub Pages.

Edit the copy in `_src/lang_*.py`, then rebuild:

    python3 _src/build.py

Shot names and the disclaimer are read from the app's own source
(`PADL_APP`, default `~/claude/Padl`), so the site says what the app says.
When the app is live, put its App Store address in `STORE_URL` in `_src/build.py`.
