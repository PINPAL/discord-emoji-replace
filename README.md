# Installation
1. Install [OpenASAR - Discord CSS Injector](https://openasar.dev/) (or any other tool capable of injecting CSS into Discord)
2. Add the following to your CSS Config:
```css
@import url(https://pinpal.github.io/discord-emoji-replace/emoji-replacement.css);
```

# Building
1. Go to https://emojipedia.org/apple
2. Keep scrolling to load all the assets
3. Download all the assets using the DevTools of your Browser
4. Place all the .webp files for the emojis under `./emojis-download`
5. Run the `generate_css.py` script

# Coming Soon
**Dynamically building using the Unicode API (no need to manually download all the files)**

See the `/generate-from-unicode-api/` folder, while this is mostly working there a few issues regarding the emojipedia URL being different on certain emojis.
