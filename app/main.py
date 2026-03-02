import discord
import requests
import tempfile
from config import DISCORD_TOKEN, THRESHOLD, TARGET_CHANNEL_ID
from clip_model import predict

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

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
                    f"🚨👮 匂わせ警察です。\n"
                    f"当画像は匂わせの疑いがあります。\n"
                    f"スコア: {score:.3f}\n"
                    f"これは警告です。今後の投稿に注意してください。"
                )

        except Exception as e:
            print(f"[ERROR] {e}")

client.run(DISCORD_TOKEN)
