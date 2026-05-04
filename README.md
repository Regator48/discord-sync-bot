# Discord Sync Bot

> Built with AI vibe coding 🧙‍♂️

A Discord bot to sync messages between channels across different servers.

## Setup

1. **Create Discord Bot**
   - Go to https://discord.com/developers/applications
   - Create new application → Bot
   - Enable Message Content Intent
   - Copy bot token

2. **Invite Bot**
   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=277025664&scope=bot%20applications.commands
   ```

3. **Install Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install discord.py
   ```

4. **Configure**
   - Create `.env` file: `DISCORD_TOKEN=your_token_here`
   - Or edit `discord-sync.service` with your token

5. **Run**
   ```bash
   ./start.sh
   ```

## Commands

- `/link <channel_id>` - Link current channel to another (by ID)
- `/unlink <channel_id>` - Remove link
- `/links` - Show linked channels
- `/channelid` - Get current channel ID
- `/ping` - Pong!
- `/syncexisting <channel_id> [limit]` - Sync past messages

## Usage

1. Add bot to both servers
2. In target server, run `/channelid` to get the channel ID
3. In source server, run `/link <channel_id>`
4. Messages will sync between the channels

## Auto-start (Linux)

```bash
sudo cp discord-sync.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-sync
sudo systemctl start discord-sync
```