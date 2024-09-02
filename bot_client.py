from pyrogram import Client
from dotenv import load_dotenv

import os


load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
channel_id = int(os.getenv("CHANNEL_ID"))


bot = Client(
	name="mybot",
	api_id=api_id,
	api_hash=api_hash,
	bot_token=bot_token
	)
