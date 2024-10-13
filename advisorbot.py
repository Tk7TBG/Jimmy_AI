from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

from discord.ext.commands import Bot

# Step 0 load our token from somewhere safe
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
# print(TOKEN) # This shows that the thing Works

# Step 1: Bot setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

bot = Bot(command_prefix="/", intents=intents)

# Step 2: message functionality
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('Message was empty because intents were not enabled property')
        return
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
         async with message.channel.typing():  # Show typing indicator
            response: str = get_response(user_message)
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# Step 3 Handling the startup of the bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running')

# Step 4 Handling Incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'{username}, {user_message}, {channel}')
    await send_message(message, user_message)

# Step 5 Main entry point
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()