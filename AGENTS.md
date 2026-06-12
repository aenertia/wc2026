# World Cup 26 Wallchart — Knowledge Base

**Generated:** 2026-06-12  
**Commit:** c9f7ef9  
**Branch:** main

## OVERVIEW

Single-file interactive FIFA World Cup 2026 wallchart. Zero-dependency vanilla HTML/CSS/JS. No framework, no build step, no package manager, no server required. Hosted on GitHub Pages.

## STRUCTURE

```
wc2026/
├── index.html                      # THE APP (1500+ lines — CSS + JS inline)
├── download_assets.py              # Asset pre-fetcher (rosters, flags, anthems, photos)
├── README.md
├── assets/
│   ├── silhouettes/                # 4 position SVGs (gk, df, mf, fw)
│   └── teams/{slug}/              # Per-team: roster.json, country.json, anthem.json, flag.svg, anthem.m4a
└── .claude/launch.json
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Change UI / layout / styling | `index.html` lines 10–308 | `<style>` block; CSS custom properties on `:root` |
| Change app logic / filtering | `index.html` lines 368–864 | `<script>` block; all vanilla JS |
| Edit match schedule data | `index.html` lines 409–478 | Array `D` — 104 hardcoded matches |
| Edit venue map | `index.html` lines 372–407 | Object `VENUES` — match# → "City · Stadium" |
| Edit group/stage colors | `index.html` lines 370–371 | `GROUP_COLORS`, `STAGE_COLORS` objects |
| Team name normalization | `index.html` lines 595–605 | `NAME_MAP` — API names → display names |
| Dialog CSS | `index.html` style block | `#teamDialog`, `.td-*` classes |
| Pitch CSS | `index.html` style block | `.pitch`, `.player-card`, `.subs-strip` |
| Country profile CSS | `index.html` style block | `.country-profile`, `.cp-*`, `.cp-anthem` |
| TEAM_META mapping | `index.html` first script block | 48-team lookup |
| `showTeamDialog()` | `index.html` second script block | Dialog open/close |
| `loadTeamData()` | `index.html` second script block | Local assets, then live API fallback |
| `renderPitch()` | `index.html` second script block | Formation + player cards |
| `renderCountryProfile()` | `index.html` second script block | Demographics, anthem, lyrics |
| `inferFormation()` | `index.html` second script block | GK/DF/MF/FW ratio to formation |
| Download anthem (Invidious) | `download_assets.py` | `search_invidious_anthem()`, `download_anthem_invidious()` |
| Download roster (Wikipedia) | `download_assets.py` | `parse_wikipedia_squads()` |

## CONVENTIONS

- **Single-file app**: All HTML, CSS, and JS live in one `.html` file. Do not split without discussing.
- **No build step**: Edit → refresh. No transpilation, no bundling.
- **Static hosting**: No server required. All external APIs (ESPN, worldcup26.ir) are called directly from the browser — all support CORS.
- **CSS naming**: Flat BEM-ish classes (`.match`, `.m-home`, `.m-score`, `.gc-head`). Not strict BEM.
- **JS naming**: camelCase functions/vars. `$` is a shorthand for `getElementById`.
- **Theming**: CSS custom properties (`--pitch`, `--chalk`, `--gold`, `--line`, etc.). Dark pitch-green palette.
- **Fonts**: Google Fonts CDN — Anton (display), Archivo (body), Space Mono (mono).
- **State**: Plain object `state={stage:"",group:"",q:""}`. Manual `render()` after mutation.
- **Data format**: Match array `D` entries are `[matchNum, stage, group, date, time, home, away]`. Times are IST (UTC+1).
- **Timezone**: All kick-offs stored as Irish Summer Time strings, converted via `Intl.DateTimeFormat`. User pref in localStorage key `wc26tz`.
- **Live data**: Polls ESPN scoreboard and worldcup26.ir every 2 minutes directly from the browser.
- **Dialog**: HTML `<dialog>` + `showModal()`, built-in focus trap, Escape, backdrop.
- **Team profile data**: local `assets/teams/{slug}/` first, live APIs as fallback.
- **Anthem audio**: m4a format (broadest browser support), sourced via Invidious proxy.
- **Player photos**: TheSportsDB `strCutout` PNG preferred, Wikipedia thumbnail fallback, position silhouette last.
- **Formation**: auto-inferred from GK/DF/MF/FW counts, never hardcoded per team.

## ANTI-PATTERNS

- **Do not add npm/node dependencies** — this is intentionally zero-dependency
- **Do not use TypeScript** — vanilla JS only, no transpilation
- **Do not split CSS/JS into separate files** unless explicitly requested
- **Never substitute match data from `D` array with API data** — `D` is the canonical schedule; API provides only live scores/standings
- **Do NOT hardcode formations** — `inferFormation()` derives from squad data
- **Do NOT commit player photos** — `assets/teams/*/players/` is .gitignored

## DATA FLOW

```
ESPN scoreboard API (CORS) ─────────────────────────────────────────────── browser JS (live scores)
worldcup26.ir/get/teams (CORS) ─────────────────────────────────────────── browser JS (flags)
Wikipedia MediaWiki API (CORS) ─────────────────────────────────────────── browser JS (fallback)
GeoAPI.info (CORS) ─────────────────────────────────────────────────────── browser JS (fallback)
assets/teams/{slug}/ ───────────────────────────────────────────────────── browser JS (primary)
Invidious / TheSportsDB ────────────────────────────────────────────────── download_assets.py (offline)
```

- `fetchScores()` → ESPN API direct → populates `scores` Map → triggers `render()`
- `fetchStandings()` → worldcup26.ir direct → populates `flagByName` Map → triggers `computeStandings()`
- Knockout team names patched via `teamOverrides` Map when API reports real teams

## COMMANDS

```bash
# Run locally (any static server works)
python3 -m http.server 8191

# Open in browser
open http://localhost:8191/

# Pre-fetch all team assets (run once, or re-run with --force)
python3 download_assets.py

# Download single team
python3 download_assets.py --team brazil

# Anthems only (re-fetch from Invidious)
python3 download_assets.py --anthems-only --force

# Player photos (slow: ~45 min for 48 teams)
python3 download_assets.py --photos-only
```

## NOTES

- No tests, no CI, no linting configured
- `!important` used twice: `prefers-reduced-motion` override (line 29) and `.loser` color (line 303) — both intentional
- `console.warn` in `fetchScores` and `fetchStandings` catch blocks — only error handling, scores silently degrade
- Hosted on GitHub Pages — no server-side code, all API calls go direct from the browser
- Anthem audio files (`anthem.m4a`) are ~1-2MB each (48 teams, ~70MB total)
- Player photos are gitignored; run `download_assets.py --photos-only` after clone
- Lyrics VTT files (`anthem.*.vtt`) are small (typically 0-10KB); included in git

## GIT REMOTES

| Remote | URL | Purpose |
|--------|-----|---------|
| `upstream` | `https://github.com/Deim0s13/world-cup-2026-schedule.git` | Original project (PR target) |
