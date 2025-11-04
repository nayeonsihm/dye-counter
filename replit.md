# Karuta Dye Tracker Discord Bot

## Overview
A Python Discord bot that automatically tracks Karuta dye and bottle openings. The bot passively monitors when users use Karuta's dye/bottle commands and maintains statistics.

## Recent Changes
- **2025-11-04**: 
  - Fixed critical security vulnerability (moved hardcoded token to environment variable)
  - Added `!stats` command (alias for `!dyes`)
  - Added `!leaderboard` command (alias for `!tallydyes`)
  - Enhanced output with rich embed messages
  - Initial bot creation with passive dye tracking functionality

## Features
- **Passive Tracking**: Automatically detects when users use Karuta dye/bottle commands
- **Statistics Tracking**: Monitors total dyes, streaks, and mystic dye occurrences
- **Leaderboard System**: View top users by total dye/bottle openings
- **Rich Embeds**: Beautiful embed messages for better UI
- **Persistent Storage**: SQLite database for data persistence

## Available Commands
- `!stats` or `!dyes` - View your dye/bottle statistics
- `!leaderboard` or `!tallydyes` - View top 10 users leaderboard
- `!mystic` - Log when you get a Mystic dye (resets streak counter)
- `!add <number>` - Manually add dye/bottle openings to your count

## How It Works
The bot automatically tracks when you use these Karuta commands:
- `ku dye` / `k!u dye` / `kuse dye` / `k!use dye`
- `ku bottle` / `k!u bottle` / `kuse bottle` / `k!use bottle`

When Karuta responds to your command, the bot automatically increments your count!

## Project Architecture
- `main.py` - Main bot application with all commands and event handlers
- `karuta_tracker.db` - SQLite database for persistent storage (auto-created)
- `.env` - Environment variables (Discord token)
- Dependencies: discord.py, python-dotenv, sqlite3 (built-in)

## Setup Instructions
1. Create a Discord bot at https://discord.com/developers/applications
2. Enable "Message Content Intent" in the Bot settings
3. Copy your bot token
4. Add the token to Replit Secrets with key `DISCORD_TOKEN`
5. Invite the bot to your server with appropriate permissions
6. Run the bot and it will automatically start tracking!

## User Preferences
- Prefers passive tracking over manual entry
- Wants `!stats` and `!leaderboard` command support

## Data Storage
All tracking data is stored in `karuta_tracker.db` (SQLite) and persists across restarts.

## Statistics Tracked
- Total dyes/bottles opened
- Dyes since last Mystic
- Longest streak before Mystic
- Shortest streak before Mystic
