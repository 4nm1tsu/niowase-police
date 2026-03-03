import discord
import requests
import tempfile
import asyncio
import os
from fastapi import FastAPI
import uvicorn
import threading
from clip_model import predict

# =========================
# Configs
# =========================
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
THRESHOLD = float(os.environ.get("THRESHOLD", 0.2))
TARGET_CHANNEL_ID = int(os.environ.get("TARGET_CHANNEL_ID", 0))
APP_VERSION = os.environ.get("APP_VERSION", "v1.0.0")

# =========================
# Discord Client
# =========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# =========================
# Health Check Server (FastAPI)
# =========================
app = FastAPI()

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "discord_ready": client.is_ready()
    }

def run_health_server():
    # uvicornも別スレッドで実行
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

# =========================
# 処理ロジック (非同期ラップ)
# =========================

async def process_image_and_predict(attachment: discord.Attachment):
    """
    画像のダウンロードと推論を別スレッドで実行する
    """
    loop = asyncio.get_running_loop()
    
    try:
        # 1. 画像をメモリ/一時ファイルにダウンロード (Blocking I/O)
        # requests.getをexecutorで実行
        response = await loop.run_in_executor(None, lambda: requests.get(attachment.url, timeout=10))
        response.raise_for_status()

        # 2. 推論の実行 (Blocking CPU/GPU Task)
        # predict関数をexecutorで実行することでDiscordのループを止めない
        with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as tmp:
            tmp.write(response.content)
            tmp.flush()
            
            # ここが重い処理
            score = await loop.run_in_executor(None, predict, tmp.name)
            return score

    except Exception as e:
        print(f"[ERROR in process_image] {e}", flush=True)
        return None

# =========================
# Discord Events
# =========================

@client.event
async def on_ready():
    print(f"[READY] Logged in as {client.user}", flush=True)

@client.event
async def on_message(message: discord.Message):
    # Bot自身の発言や指定チャンネル以外を無視
    if message.author.bot:
        return
    if TARGET_CHANNEL_ID and message.channel.id != TARGET_CHANNEL_ID:
        return
    if not message.attachments:
        return

    for attachment in message.attachments:
        # 画像以外はスルー
        if not attachment.content_type or not attachment.content_type.startswith("image"):
            continue

        # 処理開始（非同期でスコア取得）
        score = await process_image_and_predict(attachment)

        if score is not None:
            print(f"[DEBUG] Result Score: {score:.3f}", flush=True)

            if score >= THRESHOLD:
                await message.reply(
                    "🚨👮 **匂わせ警察です**\n"
                    "当画像は匂わせの疑いがあります。\n"
                    f"スコア: {score:.3f}\n"
                    "これは警告です。今後の投稿に注意してください。"
                )

# =========================
# Discord Events
# =========================

@client.event
async def on_ready():
    print(f"[READY] Logged in as {client.user} (Version: {APP_VERSION})", flush=True)
    
    activity = discord.Game(name=f"匂わせ警察 {APP_VERSION}")
    await client.change_presence(status=discord.Status.online, activity=activity)

# =========================
# Startup
# =========================

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set")

    # FastAPIを別スレッドで開始
    threading.Thread(target=run_health_server, daemon=True).start()

    # Discord Bot起動
    client.run(DISCORD_TOKEN)
