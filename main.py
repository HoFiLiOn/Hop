import os
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
import config

async def join_one(client, link):
    hash_part = link.split('+')[1] if '+' in link else link.split('joinchat/')[1]
    try:
        await client(ImportChatInviteRequest(hash_part))
        me = await client.get_me()
        print(f"[+] {me.first_name} зашёл")
        return True
    except Exception as e:
        print(f"[-] Ошибка: {e}")
        return False

async def mass_join():
    sessions = [f for f in os.listdir(config.SESSION_FOLDER) if f.endswith('.session')]
    clients = []
    for sess in sessions:
        client = TelegramClient(f"{config.SESSION_FOLDER}{sess}", config.API_ID, config.API_HASH)
        await client.start()
        clients.append(client)
    
    tasks = [join_one(c, config.TARGET_LINK) for c in clients]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(mass_join())