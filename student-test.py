import discord
import logging
import stockpile
from sys import stdout

#path.append('../Discord')

from key import DiscordToken, guild_id

intents = discord.Intents.default()
intents.message_content = True

# stockpiles bot
# Designate a channel as a stockpile channel
# 

TEST_GUILD = discord.Object(id = guild_id)

class DiscordClient(discord.Client):
    
    def __init__(self, *, intents: discord.Intents, **options: any) -> None:
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
    
    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)


async def getStockpile (channel: discord.TextChannel, stockpiles):
    #first, look through stockpiles
    for id in stockpiles:
        try:
            message = await channel.fetch_message(id)
        except discord.NotFound:
            #this is normal to happen
            continue

        return id, message #this channel has a stockpile, return the id and the message
    return None, None
    #return None #this channel does not have a stockpile, return none

    #We don't have this channel in memory, now we need to search through the messages
    
    #TODO Something is wrong here, previous messages are not being loaded properly
    #messages = message async for message in channel.history(limit=123)
    #for message in messages:
    #    print(f"{stockpiles.keys()}\n")
    #    printMessage(message)
    #    if message.id in stockpiles:
    #        printMessage(message)
    #        stockpiles[message.id][0] = channel
    #        stockpiles[message.id][1] = message
    #        return message.id
    #return None

def loadStockpiles(filename = "stockpile.txt"):
    """
    Load stockpiles from file(s) based off of the file titles in filename
    """
    try:
        f = open(filename)
    except FileNotFoundError:
        f = open(filename, "x")
        f.close()
        return {}
    dictionary = dict()
    filelines = f.readlines()
    for line in filelines:
        lines = line.strip('\n')
        if lines.isspace() or lines == '': #bad data, reject it
            continue
        print (f"Loading: {lines}\n")
        tempstock = stockpile.Stockpile("temp", lines, False)
        tempstock.loadJson()
        dictionary[tempstock.messageID] = [None, None, tempstock]
    return dictionary

def printMessage(message : discord.Message, fileout = stdout):
    """
    Helper function to print out the contents of a discord message. Defaults to stdout.
    """
    
    print(f"""
    Message ID: {message.id}
    By: {message.author.display_name} ({message.author.id})

    {message.content}
    """, file=fileout)
stockpiles = loadStockpiles()
handler = logging.FileHandler(filename="student-test.log", encoding='utf-8', mode='w')       
intents = discord.Intents.default()
intents.message_content = True
client = DiscordClient(intents = intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command()
@discord.app_commands.describe(
hex="The hex the stockpile is in. Case sensitive.",
depot="The specific depot the stockpile is in. Case sensitive.",
name="The name of the stockpile. Case sensitive",
code="6 digit stockpile code"
)

async def add_code(interaction: discord.Interaction, hex: str, depot: str, name: str, code:str):
    """Adds a code to the stockpile list. In the channel it is in."""
    print("6")
    if (len(code) != 6 or not code.isdigit()):
        print("7")
        #raise ValueError("A stockpile code must be 6 numbers long.")
    if (hex == None):
        print("8")
        #raise ValueError("No hex provided.")
    if(depot == None):
        print("9")
        #raise ValueError("No location provided.")
    if(name == None):
        print("9.5")
    print("10")
    messageID, message = await getStockpile(interaction.channel, stockpiles)
    if messageID == None:
        #there is no stockpile in this channel.
        print("11")
        await interaction.response.send_message("Cannot find a stockpile here.")
        
    else:
        print("12")
        stock = stockpiles[messageID]
        stock.addStockpile(hex, depot, name, code)
        stock.saveJson()
        #message = stockpiles[messageID][1]
        text = stock.discordText()
        print (f"awaiting on uppdating message id: {message.id} to:\n{text}")
        await message.edit(content=text)
        print(f"await on message {message.id} over.")
        await interaction.response.send_message("Added code to stockpile")


@client.tree.command()
@discord.app_commands.describe(
hex="The hex the stockpile is in. Case sensitive.",
depot="The specific depot the stockpile is in. Case sensitive.",
name="The name of the stockpile. Case sensitive"
)

async def remove_code(interaction: discord.Interaction, hex: str, depot:str, name:str):
    """Removes a code from a stockpile"""
    
    messageID, message = await getStockpile(interaction.channel, stockpiles)
    if messageID == None:
        #there is no stockpile in this channel.
        await interaction.response.send_message("Cannot find a stockpile here.")
    else:
        stock = stockpiles[messageID]
        stock.removeStockpile(hex, depot, name)
        stock.saveJson()
        #message = stockpiles[messageID][1]
        text = stock.discordText()
        print (f"awaiting on uppdating message id: {message.id} to:\n{text}")
        await message.edit(content=text)
        print(f"await on message {message.id} over.")
        await interaction.response.send_message("Removed code to stockpile")

@client.tree.command()
@discord.app_commands.describe(
    name='The name of the stockpile',
)

async def new_stockpile(interaction: discord.Interaction, name: str):
    """
    Creates a new stockpile in the channel this is run.
    """
    message = await interaction.channel.send(f"__**{name}:**__")
    stock = stockpile.Stockpile(name, name + "stockpile.txt")
    stock.updateMessageID(message.id)
    stockpiles[message.id] = stock #using the message id as the overall id
    stock.saveJson()
    #TODO, delete previous stockpile in this channel from memory
    #TODO respond

@client.tree.command()
@discord.app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    print("5")
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')

client.run(DiscordToken, log_handler=handler)
