import os
import json
import asyncio
import discord
from discord import app_commands
from discord import Webhook

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"links": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

class SyncBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced commands for {self.user}")

client = SyncBot()

def get_linked_channels(source_channel_id):
    config = load_config()
    links = config.get("links", [])
    for link in links:
        if source_channel_id in link:
            return [ch for ch in link if ch != source_channel_id]
    return []

async def sync_message(message, client):
    if message.author.bot:
        return
    
    linked = get_linked_channels(message.channel.id)
    if not linked:
        return

    for channel_id in linked:
        channel = client.get_channel(channel_id)
        if not channel:
            continue
        
        if message.attachments:
            attachment = message.attachments[0]
            file = await attachment.to_file()
            await channel.send(
                content=f"**{message.author.display_name}**: {message.content or ''}",
                file=file
            )
        else:
            await channel.send(
                content=f"**{message.author.display_name}**: {message.content}"
            )

@client.event
async def on_message(message):
    await sync_message(message, client)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.tree.command()
async def link(interaction: discord.Interaction, target_channel_id: str):
    try:
        target_channel_id = int(target_channel_id.strip().replace("<#", "").replace(">", ""))
    except ValueError:
        await interaction.response.send_message("Invalid channel ID. Use format: 123456789012345678", ephemeral=True)
        return
    
    channel_id = interaction.channel.id
    target_channel = client.get_channel(target_channel_id)
    
    if not target_channel:
        await interaction.response.send_message("Channel not found. Make sure the bot is in that server!", ephemeral=True)
        return
    
    config = load_config()
    
    linked = get_linked_channels(channel_id)
    if target_channel_id in linked:
        await interaction.response.send_message("Channels already linked!", ephemeral=True)
        return
    
    found = False
    for link in config["links"]:
        if channel_id in link:
            link.append(target_channel_id)
            found = True
            break
    
    if not found:
        config["links"].append([channel_id, target_channel_id])
    
    save_config(config)
    await interaction.response.send_message(f"Linked {interaction.channel.mention} <-> {target_channel.mention}", ephemeral=False)

@client.tree.command()
async def unlink(interaction: discord.Interaction, target_channel_id: str):
    try:
        target_channel_id = int(target_channel_id.strip().replace("<#", "").replace(">", ""))
    except ValueError:
        await interaction.response.send_message("Invalid channel ID. Use format: 123456789012345678", ephemeral=True)
        return
    
    config = load_config()
    channel_id = interaction.channel.id
    
    for link in config["links"]:
        if channel_id in link and target_channel_id in link:
            link.remove(target_channel_id)
            if len(link) == 1:
                config["links"].remove(link)
            save_config(config)
            target_channel = client.get_channel(target_channel_id)
            target_mention = target_channel.mention if target_channel else f"<#{target_channel_id}>"
            await interaction.response.send_message(f"Unlinked {interaction.channel.mention} from {target_mention}", ephemeral=False)
            return
    
    await interaction.response.send_message("Channels are not linked!", ephemeral=True)

@client.tree.command()
async def links(interaction: discord.Interaction):
    config = load_config()
    channel_id = interaction.channel.id
    linked = get_linked_channels(channel_id)
    
    if not linked:
        await interaction.response.send_message("No linked channels.", ephemeral=True)
        return
    
    channel_mentions = []
    for ch in linked:
        ch_obj = client.get_channel(ch)
        if ch_obj:
            channel_mentions.append(ch_obj.mention)
        else:
            channel_mentions.append(f"<#{ch}> (unavailable)")
    
    await interaction.response.send_message(f"Linked channels: {', '.join(channel_mentions)}", ephemeral=True)

@client.tree.command()
async def channelid(interaction: discord.Interaction):
    await interaction.response.send_message(f"This channel's ID: `{interaction.channel.id}`", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not set")
        exit(1)
    client.run(token)