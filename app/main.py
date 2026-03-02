import discord
import requests
import tempfile
import threading
import os

from fastapi import FastAPI
import uvicorn

from clip_model import predict

# =========================
# Configs
# =========================

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
THRESHOLD = float(os.environ["THRESHOLD"])
TARGET_CHANNEL_ID = int(os.environ["TARGET_CHANNEL_ID"])

# =========================
# Discord Client
# =========================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# =========================
# Health Check Server
# =========================

app = FastAPI()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "discord_ready": client.is_ready()
    }


def run_health_server():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning"
    )


# 別スレッドで起動
threading.Thread(target=run_health_server, daemon=True).start()


# =========================
# Discord Events
# =========================

@client.event
async def on_ready():
    print(f"[READY] Logged in as {client.user}", flush=True)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if TARGET_CHANNEL_ID and message.channel.id != TARGET_CHANNEL_ID:
        return

    if not message.attachments:
        return

    for attachment in message.attachments:
        if not attachment.content_type:
            continue

        if not attachment.content_type.startswith("image"):
            continue

        try:
            response = requests.get(attachment.url, timeout=10)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as tmp:
                tmp.write(response.content)
                tmp.flush()

                score = predict(tmp.name)

            print(f"[DEBUG] score={score:.3f}", flush=True)

            if score >= THRESHOLD:
                await message.reply(
                    "🚨👮 匂わせ警察です。\n"
                    "当画像は匂わせの疑いがあります。\n"
                    f"スコア: {score:.3f}\n"
                    "これは警告です。今後の投稿に注意してください。"
                )

        except Exception as e:
            print(f"[ERROR] {e}", flush=True)


# =========================
# Startup
# =========================

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN is not set")

client.run(DISCORD_TOKEN)
