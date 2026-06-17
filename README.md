# jakebowers.org

## Local Development

To generate the site locally, you'll need Python 3.14+ and the dependencies listed in `pyproject.toml` (jinja2, pyyaml).

The easiest way to run locally is with [uv](https://docs.astral.sh/uv/):

```bash
uv run python generate_site.py
```

This will automatically install dependencies and run the script.

Note: The production site is built via GitHub Actions, which uses a different setup.

## vita.bib drift-check agent (macOS launchd)

`data/vita.bib` is a derived mirror of the canonical `~/repos/vita/vita.bib`
(see CLAUDE.md, "Bibliography source"). A per-user launchd agent runs a
read-only drift check weekly (Mondays at 9:00am) and posts a macOS
notification if the mirror and the canonical have diverged. It never edits
either file.

- Agent label: `org.jakebowers.vita-bib-check`
- Plist: `~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist` (machine
  config; not tracked in this repo --- recreate it from the block below)
- Runs: `bin/vita-bib-check-notify.sh`, which calls `bin/sync-vita-bib.sh`
- Log: `~/Library/Logs/vita-bib-check.log` (plus `.out.log` / `.err.log`)

In the commands below, `gui/$(id -u)` targets your logged-in user session.

### Start / load

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist
```

### Stop / unload

```bash
launchctl bootout gui/$(id -u)/org.jakebowers.vita-bib-check
```

### Modify (e.g. change the schedule)

Edit the plist, then reload it (bootout, then bootstrap):

```bash
$EDITOR ~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist
launchctl bootout    gui/$(id -u)/org.jakebowers.vita-bib-check 2>/dev/null
launchctl bootstrap  gui/$(id -u) ~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist
```

The schedule lives in the `StartCalendarInterval` block: `Weekday` is 0-7
(0 and 7 are Sunday, 1 is Monday), with `Hour` (0-23) and `Minute`. Omit a key
to mean "every" (e.g. drop `Weekday` for a daily run). Always reload after
editing, or `launchctl` keeps using the old definition. Run `plutil -lint` on
the plist first to catch XML mistakes.

### Status and run-on-demand

```bash
launchctl print gui/$(id -u)/org.jakebowers.vita-bib-check   # registration + next firing
launchctl kickstart -k gui/$(id -u)/org.jakebowers.vita-bib-check   # run it once now
```

To check drift directly without the agent (read-only):

```bash
./bin/sync-vita-bib.sh            # exit 0 if in sync, 1 if diverged
./bin/sync-vita-bib.sh --apply    # copy canonical -> mirror (see CLAUDE.md for --force)
```

### Recreate the plist

The plist is not tracked in this repo. To set the agent up on a new machine,
write this to `~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist`
(adjust the absolute paths for that machine), then run the Start command above:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>org.jakebowers.vita-bib-check</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/jwbowers/repos/jake_site_new/bin/vita-bib-check-notify.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/Users/jwbowers/Library/Logs/vita-bib-check.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/jwbowers/Library/Logs/vita-bib-check.err.log</string>
</dict>
</plist>
```

Notes: the agent fires only while the Mac is awake (a missed weekly run fires
at next wake). macOS may route the `osascript` notification through "Script
Editor" and suppress the banner if its notifications are off; the log records
every run regardless.
