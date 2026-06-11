# World Cup 26 Wallchart

A single-file interactive wallchart for all 104 matches of the 2026 FIFA World Cup (11 June – 19 July). Filter by group, stage or team, switch timezones, and see live scores update automatically.

## Features

- All 104 matches with correct IST kick-off times and dates
- Live scores and final results via the [worldcup26.ir](https://worldcup26.ir) API — no API key required, polls every 2 minutes
- In-play matches show a live score with pulsing indicator and current minute
- Full-time matches show the final score with FT stamp and losing team dimmed
- Venue (city · stadium) displayed for every match
- Filter by group, stage, or team search
- Timezone conversion — remembers your preference via localStorage
- Late-night kick-off indicator (☾)

## Running locally

All you need is a browser and a way to serve the file over HTTP. A bare `file://` path won't work due to browser fetch restrictions on the scores API.

```bash
# Python (built-in)
python3 -m http.server 8191 --directory /path/to/folder

# Node
npx serve .
```

Then open `http://localhost:8191/world-cup-2026-schedule_1.html`.

## Running as an interactive desktop wallpaper (macOS)

This setup uses [Plash](https://apps.apple.com/app/plash/id1494023538) to render the wallchart as a live, interactive macOS wallpaper that survives reboots and sleep.

### 1. Serve the file on login

Create a launchd agent so the HTTP server starts automatically and restarts if it ever dies:

```bash
cat > ~/Library/LaunchAgents/dev.pleathen.wallchart-server.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>dev.pleathen.wallchart-server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>-m</string>
    <string>http.server</string>
    <string>8191</string>
    <string>--directory</string>
    <string>/Users/YOUR_USERNAME/Projects/fifa-wc-2026-wallpaper</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/wallchart-server.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/wallchart-server.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/dev.pleathen.wallchart-server.plist
```

Replace `YOUR_USERNAME` with your macOS username. The agent loads at login and restarts automatically if the process exits.

### 2. Configure Plash

1. Install Plash from the [Mac App Store](https://apps.apple.com/app/plash/id1494023538)
2. Click the Plash menu bar icon → **Add Website…**
3. Enter `http://localhost:8191/world-cup-2026-schedule_1.html`
4. Click the Plash menu bar icon → **Browsing Mode** to bring the wallchart to the front and interact with it (filters, search, scroll). Toggle it off to send it back behind your windows
5. Click the Plash menu bar icon → **⋯** → **Settings…** → enable **Launch at Login**

### 3. Blend the edges (optional)

Set your macOS wallpaper to a solid `#0c1713` so the page background matches seamlessly.

### Stopping the server

```bash
launchctl unload ~/Library/LaunchAgents/dev.pleathen.wallchart-server.plist
```

## Data sources

| Data | Source |
|------|--------|
| Match schedule & times | Verified against Sky Sports BST kick-off times |
| Live scores & results | [worldcup26.ir](https://worldcup26.ir) (free, no key) |
| Venues | worldcup26.ir stadiums endpoint |
