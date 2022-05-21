import asyncio
import discord
import os
from time import sleep
import requests
import json
import shutil
import ascii_image as asc

import discord
from discord.ext import commands
from dotenv import load_dotenv

os.chdir("D:/Repo/DiscordBot/") # Change this to your bot's directory

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix="!")
client.remove_command('help')

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def delete_cve():
    if os.path.exists("vulns.txt"):
        os.remove("vulns.txt")

def delete_image():
    if os.path.exists("image.jpg"):
        os.remove("image.jpg")

def delete_ascii():
    if os.path.exists("ascii_art.txt"):
        os.remove("ascii_art.txt")


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    delete_image()
     
@client.command()
async def help(msg):
    author = msg.message.author.mention

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name="Help")
    embed.add_field(name="!ping", value="Returns the instant delay")
    embed.add_field(name="!inspire", value="Returns random inspirational quotes using API.", inline=True)
    embed.add_field(name="!save", value="Use this command in the comment box when uploading an image to save the image.", inline=True)
    embed.add_field(name="!ascii", value="Creates ascii art using saved image (Deletes the saved image after it's done.)", inline=True)
    embed.add_field(name="!cve", value="(ADMIN) Searchs exploits with user input using API.", inline=True)

    await msg.send(author, embed=embed)

@client.command()
async def ping(msg):
    await msg.send(f'Latency is: {round(client.latency * 1000)} ms')


@client.command()
async def inspire(msg):
    quote = get_quote()
    await msg.send(quote)

@client.command(pass_context=True)
#!! If you want this command available for everyone, just delete the line under this one
@commands.has_guild_permissions(ban_members=True) # Only available for admins or moderators that can ban members
async def cve(msg):

    await msg.send("Which keyword do you want to search?")

    keyword = await client.wait_for("message", timeout=60)

    params = {'keyword': keyword.content, 'startIndex': 0,
              'resultsPerPage': 100}

    resp = requests.get('https://services.nvd.nist.gov/rest/json/cves/1.0/', params=params)
    data = resp.json()

    count = 0
    total_results = data['totalResults']
    f = open('vulns.txt', 'a')

    while count < total_results:
        f.write("{0} - {1}".format(data['result']['CVE_Items'][count]['cve']['CVE_data_meta']['ID'], data['result']['CVE_Items'][count]['cve']['description']['description_data'][0]['value']))
        f.write('\n')
        count += 1
    f.close()

    f = open('vulns.txt', 'r')
    lines = f.readlines()
    for line in lines:
        await msg.send(line)
    f.close()
    delete_cve()

@client.command()
async def save(msg):
    try:
        url = msg.message.attachments[0].url
    except IndexError:
        print("Error: No attachments")
        await msg.send("No attachments detected!")
    else:
        if url[0:26] == "https://cdn.discordapp.com":
            r = requests.get(url, stream=True)
            imageName = "image.jpg"
            with open(imageName, 'wb') as out_file:
                print('Saving image: ' + imageName)
                shutil.copyfileobj(r.raw, out_file)
            await msg.send("File saved succesfully.")

@client.command()
async def ascii(msg):
    await msg.send("What width would you like to use for ascii art?")
    await msg.send("Recommend width is between 10-400")
    try:
        width_input = await client.wait_for("message", timeout=60, check=lambda message: message.author == msg.author)
        width_input.content = int(width_input.content)

        await msg.send("Which characters preset do you want to use?")
        await msg.send("Type 1 or 2 or 3 or 4")
        await msg.send("1. ( @ # $ % ? * + ; : , . )")
        await msg.send("2. ( B S # & @ $ % * ! : . )")
        await msg.send("3. ( @ J D % * P + Y $ , . )")
        await msg.send("4. ( ' ( ) , - . / : ; [ ] _ ` { | } ~ )")

        try:
            character_input = await client.wait_for("message", timeout=60, check=lambda message: message.author == msg.author)
            if int(character_input.content) == 1:
                new_chars = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."] #default
            elif int(character_input.content) == 2:
                new_chars = ["B", "S", "#", "&", "@", "$", "%", "*", "!", ":", "."]
            elif int(character_input.content) == 3:
                new_chars = ["@", "J", "D", "%", "*", "P", "+", "Y", "$", ",", "."]
            elif int(character_input.content) == 4:
                new_chars = ["'", "(", ")", ",", "-", ".", "/", ":", ";", "[", "]", "_", "`","{", "|", "}", "~"]
            else:
                new_chars = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."]
                await msg.send("You had to type 1 or 2 or 3 or 4")
                await msg.send("But you wrote ({}). So it will use the deafult option.".format(character_input.content))

            try:
                asc.ascii_method(int(width_input.content), chars=new_chars)
                with open("ascii_art.txt", "rb") as f:
                    await msg.send(file=discord.File(f, "ascii_art.txt"))
                    sleep(5)
                    delete_image()
            except FileNotFoundError:
                await msg.send("You have to save image using !save command")
                await msg.send("Just copy paste an image and add !save as a comment.")

        except asyncio.TimeoutError:
            await msg.send("You did not choose any characters preset.")
            await msg.send("Process cancelled.")

        except ValueError:
            await msg.send("You have to type 1 or 2 or 3 or 4")
            await msg.send("But you wrote ({}) which is {}. It has to be an integer.".format(character_input.content, type(character_input.content)))
            await msg.send("Process cancelled.")


    except asyncio.TimeoutError:
        await msg.send("You did not give a width.")
        await msg.send("Process cancelled.")

    except ValueError or TypeError:
        await msg.send("You have to type an integer for width input. Recommended width is between (10-400)")
        await msg.send("But you wrote ({}) which is {}. It has to be an integer.".format(width_input.content, type(width_input.content)))
        await msg.send("Process cancelled.")
        
    
    delete_ascii()



client.run(TOKEN.strip("{}"))