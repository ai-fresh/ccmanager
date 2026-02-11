<p align="center">
  <img src="assets/logo.png" width="128" height="128" alt="CC Gate Logo">
</p>

<h1 align="center">CC Gate</h1>

<p align="center">
  <strong>Monitor and manage Claude Code sessions from your macOS menu bar.</strong><br>
  Auto-approve tool permissions, track active sessions, and handle Claude's questions — without leaving your workflow.
</p>

<p align="center">
  <a href="https://github.com/ai-fresh/ccgate/releases/tag/latest"><img src="https://img.shields.io/github/v/release/ai-fresh/ccgate?style=flat-square&color=blue" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/macOS-13.0%2B-blue?style=flat-square" alt="macOS 13.0+">
  <img src="https://img.shields.io/badge/Swift-5.9-orange?style=flat-square" alt="Swift 5.9">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#auto-accept-tiers">Auto-Accept</a> ·
  <a href="#faq">FAQ</a>
</p>

---

<p align="center">
  <img src="assets/screenshots/main-window.png" width="280" alt="CC Gate — Project list with live session status">
  &nbsp;&nbsp;&nbsp;
  <img src="assets/screenshots/questions-window.png" width="400" alt="CC Gate — Auto-Accept tiers and question management">
</p>

<p align="center">
  <sub>Left: Menu bar popup with project list, session counts, and status indicators. Right: Questions window with 4-tier auto-accept control and live stats.</sub>
</p>

---

## Why CC Gate?

If you use [Claude Code](https://claude.ai/code), you know the drill — every file read, every shell command, every edit requires manual approval in the terminal. CC Gate sits in your menu bar and handles that for you, so Claude can keep working while you focus on what matters.

- **No more "Allow Bash?"** — Set permission tiers and let CC Gate auto-approve trusted operations
- **See everything at a glance** — Live status for all your Claude Code sessions in one place
- **Stay in control** — Review and respond to Claude's questions from a clean native UI

## Features

### Live Session Monitoring

All your Claude Code projects in one place. Each project shows:
- **Real-time status** — active (green dots), waiting for input (red bell), or idle (orange dots)
- **Last activity** — "1s ago", "2m ago", "1d ago"
- **Session count** — how many Claude Code sessions are running per project
- **Quick search** — filter projects instantly with the search bar

### 4-Tier Auto-Accept Permissions

Granular, hierarchical control over what Claude can do without asking:

| Tier | Tools | Risk |
|:-----|:------|:-----|
| **Read** | Read, Glob, Grep, WebSearch, WebFetch | Minimal — read-only |
| **Write** | Edit, Write, MultiEdit, NotebookEdit | Low — reversible with git |
| **Execute** | Bash (all terminal commands) | High — full shell access |
| **Plan** | ExitPlanMode | Minimal — approves plans |

Each tier is an independent toggle. Unknown tools always require manual approval.

### Question Management

When Claude asks for permission, CC Gate shows it instantly:
- **Pending questions** appear in real-time with project context
- **One-click approve/deny** from the native UI
- **Auto-accept stats** — track how many operations were auto-approved (e.g., "719 auto-accepted")
- **History view** with timestamps and decision log

### Hook-Based Architecture

CC Gate integrates with Claude Code through its native **PermissionRequest hook** — no hacks, no terminal scraping:

```
Claude Code ──→ Permission Hook ──→ CC Gate ──→ Allow / Deny
                                       │
                                  Auto-accept
                                  (if tier enabled)
```

The hook is installed and managed entirely through the app UI. No manual config.

### Additional Features

- **Floating windows** — Settings, Questions, and Project List windows stay on top
- **Launch at Login** — start CC Gate automatically when you log in
- **One-click project opening** — launch any project in Terminal, VS Code, Cursor, iTerm, or Warp
- **New project creation** — create Claude Code projects directly from the menu bar
- **Auto-update checker** — get notified when a new version is available
- **Polish & English** localization

## Installation

### Download (PKG Installer — Recommended)

1. Download `CC Gate-X.Y.Z.pkg` from the [latest release](https://github.com/ai-fresh/ccgate/releases/tag/latest)
2. Right-click the `.pkg` file → **Open** → click **Open** in the dialog (one-time macOS Gatekeeper step)
3. Click **Continue** → **Install** → enter your password
4. CC Gate launches automatically — you're ready

> The PKG installer handles everything: copies to `/Applications/`, removes quarantine, and launches the app. Updates work the same way — download the new PKG and run it.

<details>
<summary><strong>Alternative: DMG install</strong></summary>

1. Download `CC Gate-X.Y.Z.dmg` from the [latest release](https://github.com/ai-fresh/ccgate/releases/tag/latest)
2. Open the DMG and drag **CC Gate** to `/Applications/`
3. Run once in Terminal:
   ```bash
   xattr -cr "/Applications/CC Gate.app"
   open "/Applications/CC Gate.app"
   ```

</details>

## Quick Start

1. **Click the terminal icon** in your menu bar to open CC Gate
2. **Install the hook** — Settings → Hook → Install (one-time setup)
3. **Configure auto-accept** — open Questions window (bell icon) and toggle the tiers you want
4. **Start coding** — CC Gate monitors your sessions automatically

That's it. All Claude Code sessions from `~/.claude/projects/` will appear in the project list with live status.

## Auto-Accept Tiers

<details>
<summary><strong>Detailed tool mapping</strong></summary>

| Tier | Tools |
|:-----|:------|
| Read | `Read`, `Glob`, `Grep`, `WebSearch`, `WebFetch`, `LS`, `Task`, `TodoRead` |
| Write | `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `TodoWrite` |
| Execute | `Bash` (all terminal commands) |
| Plan | `ExitPlanMode` |

</details>

> [!TIP]
> For most workflows, enabling **Read + Write** gives a good balance of speed and safety. Enable **Execute** only when you trust the codebase fully.

## Session Status

| Indicator | Status | Meaning |
|:---------:|:-------|:--------|
| 🟢 | Active | Claude is working (updated < 60s ago) |
| 🔔 | Waiting | Claude has a pending question |
| 🟠 | Idle | No recent activity (> 60s) |

## Settings

CC Gate includes a full Settings window with four tabs:

- **General** — launch at login, new projects folder, default app (Terminal/VS Code/Cursor/iTerm/Warp), refresh interval, question expiration
- **Permissions** — Accessibility and Automation permission status with one-click setup
- **Hook** — install/uninstall the permission hook, view status
- **About** — version info, update checker, feature overview

## Requirements

- **macOS 13.0** (Ventura) or later
- **Claude Code CLI** installed and configured
- Internet connection for initial setup

## FAQ

<details>
<summary><strong>Is it safe to auto-accept Execute (Bash)?</strong></summary>

The Execute tier gives Claude full terminal access — it can run any command. Only enable this if you trust the codebase and Claude's judgment. For most workflows, enabling Read + Write is a good balance of speed and safety.

</details>

<details>
<summary><strong>Does CC Gate work with multiple projects?</strong></summary>

Yes. CC Gate monitors all Claude Code sessions in `~/.claude/projects/` and displays them in a single list with per-project status. In the footer you can see total project count and status breakdown.

</details>

<details>
<summary><strong>What happens if CC Gate is closed?</strong></summary>

Claude Code falls back to its default behavior — asking for permission in the terminal. CC Gate is purely additive; closing it changes nothing about how Claude Code works.

</details>

<details>
<summary><strong>Can I use it without auto-accept?</strong></summary>

Absolutely. Keep all tiers disabled and use CC Gate purely as a session monitor and question management UI.

</details>

<details>
<summary><strong>The hook shows "not installed" after updating</strong></summary>

The hook signature changed in v2.6.0. Go to Settings → Hook → Uninstall, then Install again. This is a one-time step after the update.

</details>

<details>
<summary><strong>What data does CC Gate collect?</strong></summary>

CC Gate reads session data from `~/.claude/projects/` (local files only). The hook exchanges question/answer files via `~/.claude/.ccmanager/`. No data is sent to external servers beyond the initial email authentication check.

</details>

## Contributing

Contributions are welcome! The source code is available at [ccgate-source](https://github.com/ai-fresh/ccgate-source).

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with SwiftUI for the Claude Code community</sub>
</p>
