from keep_alive import keep_alive

keep_alive()

import discord
from discord.ext import commands
import sqlite3
import os
import asyncio
from flask import Flask

# === Keepalive (for Replit/Hosting) ===
app = Flask(__name__)


@app.route('/')
def home():
    return "Bot is running..."


def run():
    app.run(host='0.0.0.0', port=8080)


import threading

threading.Thread(target=run).start()

# === Intents ===
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Database setup ===
conn = sqlite3.connect("users.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    dyes INTEGER DEFAULT 0,
    mystics INTEGER DEFAULT 0,
    since_last_mystic INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    shortest_streak INTEGER DEFAULT NULL
)
""")
conn.commit()

# === Karuta Bot ID ===
KARUTA_ID = 646937666251915264


# === Utility Functions ===
def get_stats(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id), ))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (str(user_id), ))
        conn.commit()
        row = (str(user_id), 0, 0, 0, 0, None)
    return row


def update_dye_count(user_id):
    user_id = str(user_id)
    cur.execute(
        "SELECT dyes, mystics, since_last_mystic, longest_streak, shortest_streak FROM users WHERE user_id = ?",
        (user_id, ))
    row = cur.fetchone()
    if not row:
        dyes, mystics, since_last_mystic, longest, shortest = 0, 0, 0, 0, None
    else:
        dyes, mystics, since_last_mystic, longest, shortest = row

    dyes += 1
    since_last_mystic += 1

    cur.execute(
        """
    INSERT INTO users (user_id, dyes, mystics, since_last_mystic, longest_streak, shortest_streak)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        dyes=?,
        since_last_mystic=?;
    """, (user_id, dyes, mystics, since_last_mystic, longest, shortest, dyes,
          since_last_mystic))
    conn.commit()


def update_mystic_count(user_id):
    user_id = str(user_id)
    cur.execute(
        "SELECT dyes, mystics, since_last_mystic, longest_streak, shortest_streak FROM users WHERE user_id = ?",
        (user_id, ))
    row = cur.fetchone()
    if not row:
        dyes, mystics, since_last_mystic, longest, shortest = 0, 0, 0, 0, None
    else:
        dyes, mystics, since_last_mystic, longest, shortest = row

    mystics += 1
    if since_last_mystic > longest:
        longest = since_last_mystic
    if shortest is None or since_last_mystic < shortest:
        shortest = since_last_mystic
    since_last_mystic = 0

    cur.execute(
        """
    INSERT INTO users (user_id, dyes, mystics, since_last_mystic, longest_streak, shortest_streak)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        dyes=?,
        mystics=?,
        since_last_mystic=?,
        longest_streak=?,
        shortest_streak=?;
    """, (user_id, dyes, mystics, since_last_mystic, longest, shortest, dyes,
          mystics, since_last_mystic, longest, shortest))
    conn.commit()


# === Bot Events ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):
    # Only care about messages from Karuta
    if message.author.id == KARUTA_ID:
        content = message.content.lower()
        embed_text = " ".join((e.description or "") + " " + (e.title or "")
                              for e in message.embeds).lower()

        # Detect dye obtained
        if "dye obtained" in content or "dye obtained" in embed_text:
            user = None

            # Try to find who opened the dye
            if message.reference:
                try:
                    replied = await message.channel.fetch_message(
                        message.reference.message_id)
                    user = replied.author
                except Exception:
                    user = None
            elif message.mentions:
                user = message.mentions[0]

            if user:
                update_dye_count(user.id)
                print(f"✅ Logged dye for {user.display_name}")

                # Mystic detection
                if "mystic" in embed_text:
                    update_mystic_count(user.id)
                    print(f"💜 Logged MYSTIC for {user.display_name}")

    await bot.process_commands(message)


# === Commands ===
@bot.command()
async def stats(ctx):
    row = get_stats(ctx.author.id)
    _, dyes, mystics, since_last, longest, shortest = row

    embed = discord.Embed(title=f"{ctx.author.display_name}'s Stats",
                          color=discord.Color.blue())
    embed.add_field(name="Total Dyes", value=str(dyes), inline=True)
    embed.add_field(name="Mystics", value=str(mystics), inline=True)
    embed.add_field(name="Since Last Mystic",
                    value=str(since_last),
                    inline=True)
    embed.add_field(name="Longest Streak", value=str(longest), inline=True)
    embed.add_field(name="Shortest Streak",
                    value=str(shortest) if shortest is not None else "N/A",
                    inline=True)
    await ctx.send(embed=embed)


@bot.command()
async def mystic(ctx):
    update_mystic_count(ctx.author.id)
    await ctx.send(f"💜 {ctx.author.mention} logged a **Mystic Dye!**")


@bot.command()
async def add(ctx, number: int):
    user_id = str(ctx.author.id)
    cur.execute(
        "SELECT dyes, mystics, since_last_mystic, longest_streak, shortest_streak FROM users WHERE user_id = ?",
        (user_id, ))
    row = cur.fetchone()
    if not row:
        dyes, mystics, since_last, longest, shortest = 0, 0, 0, 0, None
    else:
        dyes, mystics, since_last, longest, shortest = row
    dyes += number
    since_last += number
    cur.execute("UPDATE users SET dyes=?, since_last_mystic=? WHERE user_id=?",
                (dyes, since_last, user_id))
    conn.commit()
    await ctx.send(f"✅ Added {number} dyes to {ctx.author.mention}'s count!")


@bot.command()
async def leaderboard(ctx):
    cur.execute("SELECT user_id, dyes FROM users ORDER BY dyes DESC LIMIT 10")
    rows = cur.fetchall()

    embed = discord.Embed(title="🏆 Dye Leaderboard",
                          color=discord.Color.gold())
    for i, (user_id, dyes) in enumerate(rows, start=1):
        try:
            user = await bot.fetch_user(int(user_id))
            embed.add_field(name=f"{i}. {user.display_name}",
                            value=f"{dyes} dyes",
                            inline=False)
        except:
            embed.add_field(name=f"{i}. Unknown User",
                            value=f"{dyes} dyes",
                            inline=False)
    await ctx.send(embed=embed)


# === Run bot ===
bot.run(os.getenv("TOKEN"))
