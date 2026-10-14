# Obsidian theme constraints: a template for designing new themes

This document lists everything known to limit the design and publishing of an Obsidian **app theme**. Hand it to a designer (or Claude Design) before a new theme is drawn, so the design fits the store from the start.

It comes from two themes accepted into the official community directory (Pastello, Harvest) and from the official docs, checked 2026-10-14. Each rule says where it comes from:

- **[Official]**: Obsidian's docs. Breaking it blocks publication.
- **[Review]**: the store's automated review. It reports warnings or errors you have to fix before the theme can be installed.
- **[Practice]**: our own standard, or a lesson learned the hard way. Not enforced by Obsidian, but break it only on purpose.

Official sources:
- Build a theme: https://docs.obsidian.md/Themes/App+themes/Build+a+theme
- Theme guidelines: https://docs.obsidian.md/Themes/App+themes/Theme+guidelines
- Submit a theme: https://docs.obsidian.md/themes/app-themes/submit-theme
- Manifest: https://docs.obsidian.md/Reference/Manifest
- CSS variables: https://docs.obsidian.md/Reference/CSS+variables/CSS+variables

---

## 1. What a theme is

- A theme is **one CSS file** (`theme.css`) plus a `manifest.json`. Nothing else ships. **[Official]**
- **No JavaScript.** A theme can't read the date, the time, the file name or settings, and it can't add DOM elements. Anything that changes "automatically" (seasonal modes, time-of-day palettes) is impossible in a theme. Drop it from the design, or make it a manual option. **[Official]**
- Everything visible must be expressible in CSS: variables, selectors on Obsidian's existing DOM, pseudo-elements (`::before` / `::after`) and background images. A design element that needs new markup (for example a "FILES" label above the explorer) can't be built.
- The theme must look right in **both light and dark mode**, which follow Obsidian's own Appearance setting (`.theme-light` / `.theme-dark`). The theme can't force one or the other, and it shouldn't add its own light/dark toggle. **[Official]**

## 2. Store and publishing rules

### Repository and files [Official]
- Public GitHub repo. These files go at the **repo root** (not in a subfolder):
  - `theme.css`
  - `manifest.json`
  - `README.md`: an excerpt shows on the listing page; relative images are resolved against the repo
  - `LICENSE`
  - a screenshot, recommended **512 × 288 px** (we name it `screenshot.png`)

### Manifest [Official]
| Field | Required | Notes |
|---|---|---|
| `name` | yes | **Can't be changed after submission. Can't contain the word "Theme".** Must be unique in the directory (check `community-css-themes.json` in `obsidianmd/obsidian-releases`). |
| `version` | yes | Semantic versioning, `x.y.z` only. |
| `minAppVersion` | yes | Oldest supported Obsidian. It also sets the browser target of the lint (see §3). |
| `author` | yes | |
| `authorUrl` | no | |
| `fundingUrl` | no | |

### Releases [Official]
- Each version is a GitHub release whose **tag equals `version` exactly** (`1.0.0`, no `v` prefix), with `manifest.json` and `theme.css` attached as assets.
- The directory reads `manifest.json` from the default branch HEAD, and installs download from the matching release.
- Submit once at https://community.obsidian.md. Later releases are picked up automatically, no resubmission.
- Review is automatic. To fix a problem, publish a new release with a higher version.

## 3. Technical limits on the CSS

### No network, no remote assets [Official]
- `theme.css` must not load anything remote: no `http://`, `https://` or `@import`. Fonts and images must be **embedded** (base64 / data URIs) or not used.
- Design consequence: every custom font and every image costs file size (see below).

### No `!important` [Official]
- It stops users overriding the theme with snippets. Keep selectors simple and low-specificity.

### Use Obsidian's CSS variables [Official]
- Prefer overriding Obsidian's variables (`--background-primary`, `--h1-size`, `--nav-item-*`, `--code-*`, `--callout-*`…) over restyling elements. This keeps hover, active and selected states working.
- General variables go on `body`; color variables on `.theme-light` / `.theme-dark`.
- Design consequence: design in terms of **tokens that map onto Obsidian variables**. A design that matches Obsidian's structure costs little; one that restyles everything costs size and breaks between versions.

### File size: under 100 KB [Review]
- The review warns on large files; we keep `theme.css` **under 100 KB**.
- Measured budget (Harvest 1.0.1, 54 KB on disk, 4 palettes, all decor, no fonts):
  - all CSS rules, variables and the Style Settings block: ~26 KB
  - 40 inline SVG data URIs: ~28 KB. Single icons are 0.5–1.4 KB, composed decor scenes up to ~2 KB. Each one is **multiplied by every palette and variant it's colored for**: a variant only costs new copies of the icons whose colors differ from the base palette. Fewer distinct icon colors = smaller file.
  - fonts (Harvest, before they were dropped): DM Sans + Literata subset, base64 WOFF2 = **55.7 KB**, more than half the budget. The original design handoff estimated 150–300 KB for three families.
- Rule of thumb: **colors, icons and decoration beat fonts.** Name the fonts in the stack (`'DM Sans', …`) and let them apply if the user has them installed, rather than embedding them. Users set body, interface and code fonts in Settings → Appearance. Headings have no Obsidian setting, so offer a Style Settings text field for the heading font. Embed at most one small family, and only if decoration leaves room.

### Store lint: `stylelint-config-obsidianmd` [Review]
The review runs the official stylelint config; target is **0 warnings**. Its browser-support rule checks against the Chromium of `minAppVersion` (1.5.0 = Chrome 114). With that target it flags:
- **every `mask*` property** (`mask-image`, `-webkit-mask`…). So icons **can't** be recolored with masks. Use pre-colored SVG backgrounds (one per color/palette, generated by a build script) or an icon font colored with `color`.
- **every `text-decoration-*` property** and `text-decoration` with a style value (`dotted`, `wavy`). So no dotted/wavy/colored underlines through `text-decoration`. Use `border-bottom` instead (e.g. `1px dotted currentcolor`). Plain `text-decoration: underline` and `text-underline-offset` are fine.
- Raising `minAppVersion` changes what's allowed, but drops users on older Obsidian. Decide that on purpose.
- Only the lint's **warnings** mirror the review. The style errors it prints come from `stylelint-config-standard` and the review ignores them.

### Accent color [Review feedback]
- Obsidian has a user **accent color picker**. Don't override it: the theme only sets the default `--accent-h/s/l`. Buttons, selection, toggles and other interactive elements follow the user's accent.
- Design consequence: things whose color is part of the identity (headings, links, folders, syntax, decoration) must use the theme's **own fixed tokens**, not the accent. The design should still look good if the user picks a different accent (e.g. blue).
- Text on accent-colored buttons must work for both light and dark accents (the theme picks dark or light ink from the accent's lightness; Harvest switches to dark ink above 55% lightness).
- The default accent itself must reach 4.5:1 against its button ink. Harvest's light accent had to be darkened for this.

### Unmapped UI stays grey [Practice]
- Modals, inputs, buttons, dropdowns and hover borders use Obsidian's neutral grey ramp (`--color-base-00` … `--color-base-100`), not the theme's tokens. If the theme only maps its own tokens, those parts stay cold grey next to a warm palette. Harvest redefines the whole ramp as steps from `bg` toward `text`.
- Design consequence: the palette needs a **full surface ramp** (or a rule to derive one), and the design should show a modal, a text input and a settings page, not only the editor and explorer.

### Must work without plugins [Practice]
- Optional settings go through the **Style Settings** plugin (a `/* @settings */` YAML block at the top of the CSS: class toggles, class-selects, color and text variables). Without the plugin the theme must look complete, so every option needs a sensible **default that applies with no class set**.

## 4. Accessibility [Practice]

Obsidian doesn't enforce contrast, but we hold every theme to **WCAG AA, 4.5:1** for all text, in **every palette and both modes**:
- body, muted, heading, link, folder and file text against the background they sit on;
- and also against secondary surfaces: sidebar, active/hovered row, tag pill, inline code, code block, callout background, button ink on the accent;
- syntax colors in code blocks, **including comments** (usually the first to fail);
- each callout title color on the callout background.

Exempt: the deliberately faint text (status bar, placeholder). Keep it faint, not invisible.

Design consequence: light-mode warm/pastel colors usually fail and need darker variants. In Harvest every dark palette passed unchanged, but six light-mode tokens had to be darkened after design (accent, h1, h4, string, and comment in both palettes). Comments went from ~3:1 to 4.5:1 and ended close to `muted`; they stay distinct through italics and a dashed box, not color. Run the numbers **while designing**, and give the light palette its own darker values rather than reusing the dark-mode hues.

Also:
- Text must stay readable over decorations: decor sits at low opacity (we used 18–60%).
- Respect the user's font size: give sizes relative to the body (em), not fixed px. Harvest's mock was measured in px at a 14px body, so every size had to be converted (e.g. H1 30px = 2.143em).

## 5. Obsidian's DOM: what can be styled and how

- **File explorer:** each row has a title element; icons go on the row's `::before`, **never inside the editable title text** (it becomes `contenteditable` when renaming and the icon breaks the caret). The DOM differs between Obsidian 1.5 and 1.12+. Folder rows have a collapse chevron that can be recolored and resized cheaply; replacing it costs more.
- **Explorer layout spec** for the design: row height, font size, padding, indent per level, icon size and gap, folder vs file text color, active row, hover row, indent guides.
- **Headings:** H1–H6 are styled through variables (size, weight, color, font, line height). Small extras like a marker before H2 are possible as `::before`. They must work in both reading view and Live Preview (the editor), which have different DOM. In Live Preview the marker sits on the editor line, next to the caret: keep it small, and verify the caret in real Obsidian.
- **Callouts:** there are many types (note, info, todo, tip, success, question, warning, failure, danger, bug, example, quote…). Harvest's handoff showed only a Note, so the other types had to be invented during development. The design should specify all of them, or at least a color rule per group, so warnings and errors stay distinguishable. Callout color handling changed in Obsidian 1.14; set full colors.
- **Inline code and code blocks share the same Obsidian variables**; the theme overrides them locally for inline code. Design both, they can differ.
- **Bullets, checkboxes, `hr`, blockquotes, tags, highlights, inline code, code blocks, links, unresolved links, `%% comments %%`** (editor only; reading view drops them): specify each.
- **Alternating patterns** (e.g. every other bullet a different leaf) are exact in reading view but only approximate in Live Preview, where non-list lines count too.
- **Every value must be specified for every mode.** Harvest's spec didn't say which color the Off-mode H2 marker used; gaps like that get guessed during development.
- Elements Obsidian doesn't have (custom labels like a "FILES" header, extra panels, brand marks in odd places) can't be added.

### Decoration placement
- Each element has only `::before` and `::after`, and Obsidian already uses some of them. In practice a pane gets **at most two decoration layers** (Harvest: a sidebar scene on `::after`, a cobweb on `::before`).
- **Explorer decor can sit behind the file tree**: the rows are transparent, so a scene at the bottom of the sidebar shows through between rows. Hovered and active rows cover it. (In Harvest 1.0.0 the leaf pile covered rows and icons; a user reported it and 1.0.1 moved it behind.)
- **Editor decor can't sit behind the text**: the editor paints an opaque background. It sits **over** the text, in a corner, at low opacity. It doesn't scroll, and in a pane narrower than the line width plus the decor width it overlaps the first lines. CSS can't hide it based on pane width. Keep it small and in the corner, and turn it off on phones.

## 6. Mobile [Practice]

Obsidian mobile uses the same `theme.css`, under `.is-mobile` (and `.is-phone`). Specify:
- tap targets of **at least 44 px** (explorer rows), 16 px tree font, wider indent;
- smaller heading scale and code size;
- code blocks scroll horizontally instead of wrapping;
- which decorations turn off on phones (corner decor usually does).

## 7. What a design handoff should contain

To keep a new theme within these rules, the handoff should include:

1. **Tokens** as a `tokens.json`: one palette per mode (light, dark, plus any variants), in `#rrggbb`, named by role (`bg`, `side`, `text`, `muted`, `faint`, `border`, `accent`, `h1`…`h6`, `link`, `tag`, `code-bg`, syntax colors, `callout-bg/border`, `folder`, `folder-text`, `file-text`…). Every text/background pair at **≥ 4.5:1**.
2. **A mapping** from tokens to Obsidian's CSS variables.
3. **Typography**: font families as stacks with fallbacks (assume they are **not embedded**), sizes as ratios of the body size.
4. **Icons as standalone SVGs** using `currentColor` (two-tone via `fill-opacity`), small and simple. No masks. Claude Design exports SVGs with C2PA provenance `<metadata>`; it was stripped from Harvest's icons (the build also strips it). Keep the explorer's native collapse chevron unless the design really needs another shape: restyling it is free, replacing it costs a data URI per palette.
5. **Decorations as SVG compositions** with sizes, positions and opacity, sized against the 100 KB budget × number of palettes. Place them per §5 "Decoration placement".
6. **Settings**: which options exist (Style Settings), with the default for no-plugin users. No time- or date-based behavior (Harvest's "Auto Halloween Oct 24–31" was dropped for this). In the `@settings` YAML, quote values YAML reads as booleans (`"Off"`, `"On"`, `"Yes"`, `"No"`).
7. **Specs for every element** in §5 and the mobile rules in §6, in every mode.
8. **Screenshots**: one 512 × 288 store thumbnail, and full-size README images per mode. Don't put the working name in the visible UI of the mockups, and don't show features that may be dropped: Harvest's title bars still said "Ember Hearth" and had to be cropped, and its settings mockup was unusable because it showed the dropped Auto Halloween toggle. Mockups are only a stopgap: the README should say so until real Obsidian captures replace them.
9. **The name**: free in the directory, without "Theme", final before the first submission (it can't change). Prefer the final name before the handoff; otherwise keep CSS prefixes neutral so only the manifest, README and settings name change.
10. **No folder layout or technique the store can't use.** Harvest's handoff asked for an `ember-hearth/` subfolder (the store reads the repo root), `mask-image` icons (lint) and three embedded fonts (size). Describe *what* to show, and leave the technique to development.

## 8. Pre-release checklist

- [ ] `theme.css` < 100 KB
- [ ] no `http://`, `https://`, `@import`, `!important`
- [ ] `stylelint-config-obsidianmd`: 0 warnings (no `mask*`, no `text-decoration-*`)
- [ ] contrast ≥ 4.5:1 on all pairs, all palettes, both modes
- [ ] works without Style Settings (defaults apply with no class)
- [ ] accent picker still works; identity colors don't depend on it
- [ ] mobile: 44 px rows, readable sizes, decor off on phones
- [ ] `manifest.json` valid, `version` bumped, name without "Theme"
- [ ] root has `README.md`, `LICENSE`, `screenshot.png` (512 × 288)
- [ ] release tag = manifest version (no `v`), with `manifest.json` and `theme.css` attached
- [ ] checked in real Obsidian, since headless renders miss these: the caret at the start of a decorated heading in Live Preview, the rename caret in the explorer, the comment box in Live Preview, the Obsidian 1.5 DOM, and the Style Settings panel
