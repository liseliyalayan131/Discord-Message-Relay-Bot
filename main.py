import discord
from discord.ext import commands, tasks
import logging
import aiohttp
import zipfile
import os
from io import BytesIO
from colorama import Fore, Style, init
from pyfiglet import figlet_format
from dotenv import load_dotenv
import ast

load_dotenv()
init(autoreset=True)

def colorize(text, color):
    colors = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE
    }
    return colors.get(color, Fore.WHITE) + text + Style.RESET_ALL

def print_ascii_art(text, color='cyan'):
    ascii_art = figlet_format(text, font='starwars')
    print(colorize(ascii_art, color))

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SOURCE_CHANNELS = ast.literal_eval(os.getenv('SOURCE_CHANNELS', '[]'))
TARGET_CHANNELS = ast.literal_eval(os.getenv('TARGET_CHANNELS', '[]'))
BOT_LOGO_URL = os.getenv('BOT_LOGO_URL', 'https://i.imgur.com/HABSi2H.png')

message_forwarding_active = True

message_map = {}

@bot.event
async def on_ready():
    print_ascii_art("Harmoni", color='green')
    print(colorize(f'{bot.user.name} olarak giriş yapıldı.', 'blue'))
    cleanup_task.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id in SOURCE_CHANNELS and message_forwarding_active:
        for target_channel_id in TARGET_CHANNELS:
            target_channel = bot.get_channel(target_channel_id)
            if target_channel:
                embed = await create_embed(message, "📩 Yeni Mesaj")
                sent_message = await target_channel.send(embed=embed)
                message_map[message.id] = sent_message.id

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if after.author.bot:
        return

    if after.channel.id in SOURCE_CHANNELS and message_forwarding_active:
        for target_channel_id in TARGET_CHANNELS:
            target_channel = bot.get_channel(target_channel_id)
            if target_channel and after.id in message_map:
                embed = await create_edit_embed(before, after)
                target_message = await target_channel.fetch_message(message_map[after.id])
                await target_message.edit(embed=embed)

@bot.event
async def on_message_delete(message):
    if message.channel.id in SOURCE_CHANNELS and message_forwarding_active:
        for target_channel_id in TARGET_CHANNELS:
            target_channel = bot.get_channel(target_channel_id)
            if target_channel and message.id in message_map:
                embed = discord.Embed(
                    title="🗑️ Mesaj Silindi",
                    description=f"{message.author.display_name} adlı kullanıcının mesajı silindi.",
                    color=discord.Color.red(),
                    timestamp=message.created_at
                )
                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                embed.set_thumbnail(url=BOT_LOGO_URL)
                embed.set_footer(text=f"{message.guild.name} | {message.channel.name}", icon_url=BOT_LOGO_URL)

                invite_link = await generate_invite(message.guild)
                if invite_link:
                    embed.add_field(name="🔗 Sunucu Davet Linki", value=invite_link, inline=False)
                
                add_guild_info(embed, message.guild)

                target_message = await target_channel.fetch_message(message_map[message.id])
                await target_message.edit(embed=embed)
                
                del message_map[message.id]

async def create_embed(message, title):
    embed = discord.Embed(
        title=title,
        description=f"```{message.content}```",
        color=discord.Color.blue(),
        timestamp=message.created_at
    )
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
    embed.set_thumbnail(url=BOT_LOGO_URL)
    embed.set_footer(text=f"{message.guild.name} | {message.channel.name}", icon_url=BOT_LOGO_URL)
   
    invite_link = await generate_invite(message.guild)
    if invite_link:
        embed.add_field(name="🔗 Sunucu Davet Linki", value=invite_link, inline=False)
    
    add_guild_info(embed, message.guild)

    if "http" in message.content:
        words = message.content.split()
        urls = [word for word in words if word.startswith("http")]
        for url in urls:
            embed.add_field(name="🔗 Link", value=url, inline=False)

    return embed

async def create_edit_embed(before, after):
    embed = discord.Embed(
        title="✏️ Mesaj Düzenlendi",
        color=discord.Color.orange(),
        timestamp=after.edited_at
    )
    embed.set_author(name=after.author.display_name, icon_url=after.author.avatar.url)
    embed.set_thumbnail(url=BOT_LOGO_URL)
    embed.set_footer(text=f"{after.guild.name} | {after.channel.name}", icon_url=BOT_LOGO_URL)

    embed.add_field(name="📜 Eski Mesaj", value=f"```{before.content or 'Boş'}```", inline=False)
    embed.add_field(name="🆕 Yeni Mesaj", value=f"```{after.content or 'Boş'}```", inline=False)

    invite_link = await generate_invite(after.guild)
    if invite_link:
        embed.add_field(name="🔗 Sunucu Davet Linki", value=invite_link, inline=False)
    
    add_guild_info(embed, after.guild)

    if "http" in after.content:
        words = after.content.split()
        urls = [word for word in words if word.startswith("http")]
        for url in urls:
            embed.add_field(name="🔗 Güncellenmiş Link", value=url, inline=False)

    return embed

async def generate_invite(guild):
    invites = await guild.invites()
    if invites:
        return invites[0].url
    else:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                invite = await channel.create_invite(max_age=0, max_uses=0)
                return invite.url
    return None

def add_guild_info(embed, guild):
    embed.add_field(name="🛡️ Sunucu İsmi", value=guild.name, inline=True)
    embed.add_field(name="👑 Sunucu Sahibi", value=guild.owner.display_name, inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=guild.member_count, inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else BOT_LOGO_URL)

@bot.command()
@commands.has_permissions(administrator=True)
async def toggle_forwarding(ctx):
    global message_forwarding_active
    message_forwarding_active = not message_forwarding_active
    status = "aktif" if message_forwarding_active else "deaktif"
    await ctx.send(f"Mesaj yönlendirme {status} hale getirildi.", delete_after=10)

@bot.command()
@commands.has_permissions(administrator=True)
async def add_channels(ctx, source_id: int, target_id: int):
    global SOURCE_CHANNELS, TARGET_CHANNELS
    SOURCE_CHANNELS.append(source_id)
    TARGET_CHANNELS.append(target_id)
    await ctx.send(f"Kaynak kanal: {source_id}, Hedef kanal: {target_id} listeye eklendi.", delete_after=10)

@bot.command()
async def status(ctx):
    status = "aktif" if message_forwarding_active else "deaktif"
    await ctx.send(f"Mesaj yönlendirme şu anda {status}. Kaynak Kanallar: {SOURCE_CHANNELS}, Hedef Kanallar: {TARGET_CHANNELS}")

@bot.command()
@commands.has_role('Admin')
async def remove_channel(ctx, channel_id: int):
    global SOURCE_CHANNELS, TARGET_CHANNELS
    if channel_id in SOURCE_CHANNELS:
        SOURCE_CHANNELS.remove(channel_id)
        await ctx.send(f"Kaynak kanallardan {channel_id} çıkarıldı.", delete_after=10)
    elif channel_id in TARGET_CHANNELS:
        TARGET_CHANNELS.remove(channel_id)
        await ctx.send(f"Hedef kanallardan {channel_id} çıkarıldı.", delete_after=10)
    else:
        await ctx.send(f"{channel_id} ID'si listede bulunamadı.", delete_after=10)

@bot.command()
@commands.has_permissions(administrator=True)
async def set_role(ctx, command_name: str, role: discord.Role):
    command = bot.get_command(command_name)
    if command:
        command.add_check(commands.has_role(role.name).predicate)
        await ctx.send(f"`{command_name}` komutu için `{role.name}` rolü ayarlandı.", delete_after=10)
    else:
        await ctx.send(f"{command_name} adında bir komut bulunamadı.", delete_after=10)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(colorize("Bu komutu kullanmak için yeterli izniniz yok.", 'red'))
    elif isinstance(error, commands.BadArgument):
        await ctx.send(colorize("Geçersiz argüman. Lütfen komutları doğru şekilde kullanın.", 'red'))
    elif isinstance(error, commands.MissingRole):
        await ctx.send(colorize("Bu komutu kullanabilmek için gerekli role sahip değilsiniz.", 'red'))
    else:
        await ctx.send(colorize("Bir hata oluştu.", 'red'))
        logging.error(colorize(f"Hata: {str(error)}", 'red'))

@tasks.loop(hours=24)
async def cleanup_task():
    for channel_id in TARGET_CHANNELS:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.purge(limit=100)
            logging.info(colorize(f" Eski mesajlar temizlendi.", 'blue'))

bot.run(DISCORD_TOKEN)