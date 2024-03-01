#https://discord.com/api/oauth2/authorize?client_id=1210697340348928101&permissions=0&scope=bot%20applications.commands

import asyncio
import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from ressources.read_google_docs import replace_google_docs_url_with_content
from ressources.read_google_sites import replace_google_sites_url_with_content
from ressources.rag import RAG

with open("KEYS/BOT_TOKEN.txt", "r", encoding="utf-8") as f:
    BOT_TOKEN = f.read()
if not BOT_TOKEN:
    BOT_TOKEN = input("Insert your Bot Token here:\n > ")

qa_channel_id = None
info_channels = []

prefix = "lib!"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)
tree = bot.tree

rag = RAG("Library", 4000)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}.')

@bot.command()
async def ping(ctx):
    response = "pong"
    await ctx.send(response)

@bot.command()
@has_permissions(administrator=True)
async def set_qa(ctx, qa_channel: discord.TextChannel, *info_channels_l):
    global qa_channel_id
    qa_channel_id = int(qa_channel.id)
    global info_channels
    info_channels = [int(c[2:-1]) for c in info_channels_l]
    await ctx.send("```QA Channel & Info Channels set.```")

@bot.command()
async def load(ctx):
    if qa_channel_id == None or len(info_channels) == 0:
        m = await ctx.reply("```First set the QA Channel and the Info Channels...```")
        return
    async with ctx.channel.typing():
        m = await ctx.reply("```Reading data available...```")
        await asyncio.sleep(1)

        info_channels_ids = info_channels

        data = []
        progression_bar_read = "|"*(int(0/len(info_channels_ids)*10))+"-"*(10-int(0/len(info_channels_ids)*10))+f" {0/len(info_channels_ids)*100}%"
        for i, id in enumerate(info_channels_ids):
            for channel in ctx.guild.channels:
                if channel.id == id:
                    await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Reading #{channel.name}...```")
                    txt = ""
                    if type(channel) == discord.ForumChannel:
                        threads = channel.threads
                        async for t in channel.archived_threads():
                            threads.append(t)
                        for thread in threads:
                            await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Reading #{channel.name}_{thread.name}...```")
                            txt = ""
                            async for c in thread.history(limit=100):
                                print(f"#{channel.name}_{thread.name}")
                                content = c.content
                                for e in c.embeds:
                                    try:
                                        try:
                                            title = dic["title"]
                                        except Exception:
                                            title = ""
                                        try:
                                            desc = dic["description"]
                                        except Exception:
                                            desc = ""
                                        content += "\n"+title+"\n"+desc+"\n"
                                    except Exception:
                                        pass
                                raw_content_google, status = replace_google_docs_url_with_content(content)
                                if status:
                                    await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Google Document detected in #{channel.name}_{thread.name} and parsed...```")
                                    await asyncio.sleep(1)
                                raw_content_google, status = replace_google_sites_url_with_content(raw_content_google)
                                if status:
                                    await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Google Site detected in #{channel.name}_{thread.name} and parsed...```")
                                    await asyncio.sleep(0.2)

                                txt += raw_content_google+"\n"
                            if len(txt) < 10:
                                await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Empty, #{channel.name}_{thread.name} ignored.```")
                            else:
                                data.append((str(channel.name+"_"+thread.name).replace('"',""), txt))
                            await asyncio.sleep(0.2)
                    else:
                        async for c in channel.history(limit=100):
                            content = c.content
                            for e in c.embeds:
                                dic = e.to_dict()
                                try:
                                    title = dic["title"]
                                except Exception:
                                    title = ""
                                try:
                                    desc = dic["description"]
                                except Exception:
                                    desc = ""
                                content += "\n"+title+"\n"+desc+"\n"
                            raw_content_google, status = replace_google_docs_url_with_content(content)
                            if status:
                                await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Google Document detected in #{channel.name} and parsed...```")
                                await asyncio.sleep(0.2)
                            raw_content_google, status = replace_google_sites_url_with_content(raw_content_google)
                            if status:
                                await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Google Site detected in #{channel.name}_{thread.name} and parsed...```")
                                await asyncio.sleep(0.2)
                            txt += raw_content_google+"\n"
                        if len(txt) < 10:
                            await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Empty, #{channel.name} ignored.```")
                        else:
                            data.append((str(channel.name).replace('"',""), txt))
                    progression_bar_read = "|"*(int((i+1)/(len(info_channels_ids))*10))+"-"*(10-int((i+1)/(len(info_channels_ids))*10))+f" {int((i+1)/(len(info_channels_ids))*100)}%"
                    await asyncio.sleep(0.2)

        await m.edit(content=f"```Reading data available...\n - {progression_bar_read}\n - Enregistrement...```")
        if not os.path.exists("Library"):
            os.makedirs("Library")
        for d in data:
            with open("Library/"+d[0]+".txt", "w", encoding="utf-8") as f:
                f.write(d[1])

        counter = 0
        pro = ["|","/","-","\\"]
        await m.edit(content=f"```Reading data available.\n - Finished.```")

        async for feed in rag.load():
            await m.edit(content=f"```Reading data available.\n - Finished.\nPre-Vectorization...\n  {pro[counter%len(pro)]}\n```")
            counter+=1

        await m.edit(content=f"```Reading data available.\n - Finished.\nPre-Vectorization...\n - Finished.\nLoaded.```")

def check(m):
    if m.reference is not None or not m.is_system:
         return True
    return False

@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)
    if bot.user.mentioned_in(message) and message.author.id != bot.user.id and not check(message):
        if qa_channel_id == None:
            m = await message.reply("```First set at least the QA Channel.```")
            return

        question = message.clean_content.replace("@"+bot.user.display_name, "")

        m =await message.reply(content=f"```Fragmentation and preliminary vector scanning...```")
        counter = 0
        pro = ["|","/","-","\\"]

        ans = ""
        asking = False
        async for feed in rag.ask(question, 6):
            if asking:
                if counter%10 == 0:
                    await m.edit(content=ans+f"\n`{pro[counter%len(pro)]}`")
                if type(feed) == list:
                    break
                ans += feed
            else:
                await m.edit(content=f"```Fragmentation and preliminary vector scanning...\n  {pro[counter%len(pro)]}\n```")
            if feed == "<|asking|>":
                asking = True
            counter+=1

        docs = ' | '.join(list(set([f.split("()")[0] for f in feed])))

        await m.edit(content=ans.replace("</s>", "")+f"\n`{docs}`")
        await m.reply(content=message.author.mention)

bot.run(BOT_TOKEN)
