#imports
import discord
import asyncio
import simpleobsws
from discord.ext import commands
import random

#variables
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host='127.0.0.1', port=4444, password='YOUR_OBS_WEBSOCKETS_PASSWORD', loop=loop) # <---remember to change host ip if on a different computer!
bot = commands.Bot(command_prefix='!')

#definitions
async def make_request(diceRoll='1d4'):
    # connect to obs
    await ws.connect() 
    # create the browser source DiceRoller in the scene LIVE
    await ws.call(
        'CreateSource', {
            'sourceName':'diceBot', 
            'sourceKind':'browser_source', 
            'sceneName':'LIVE', # <--- change to your scene
            'setVisible':True
        }
    )
    # pass settings to source
    await ws.call(
         'SetSourceSettings', {
            'sourceName':'diceBot', 
            'sourceSettings': {
                'css': '', 
                'height': 1080, # <--- change to match obs resolution
                'shutdown': True, 
                'url': 'http://dice.bee.ac/?dicehex=4E1E78&labelchex=CC9EEC&chromahex=00ff00&roll&d='+diceRoll, 
                'width': 1920 # <--- change to match obs resultion
            }
        }
    )
    # chroma key added to the source DiceRoller
    await ws.call(
        'AddFilterToSource', {
            'sourceName':'DiceRoller',
            'filterName':'Chroma Key',
            'filterType': 'chroma_key_filter', 
            'filterSettings':{
            }
        }
    )
    # how long the DiceRoller source exists
    await asyncio.sleep(7)
    # delete the source DiceRoller from the scene LIVE
    await ws.call(
       'DeleteSceneItem', {
            'scene':'LIVE', # <--- change to your scene
            'item':{
                'name':'diceBot'
            }
        }
    )
    # disconnect from OBS
    await ws.disconnect()

#commands  
# basic dice rolling command          
@bot.command(name='r', help='Simulates rolling dice. Uses d notation. ex: 3d6')
async def roll(ctx, roll):
    plus = "+"
    if plus in roll:  #check if two types of dice has been rolled (Limited to two types)
        dice = roll.split('+') #Split the two types of dice
        roll1 = dice[0].split('d') 
        roll2 = dice[1].split('d')
        number_of_dice1 = int(roll1[0])
        number_of_sides1 = int(roll1[1])

        number_of_dice2 = int(roll2[0])
        number_of_sides2 = int(roll2[1])

        dice1 = [
            str(random.choice(range(1, number_of_sides1 + 1)))
            for _ in range(number_of_dice1)
        ]
        dice2 = [
            str(random.choice(range(1, number_of_sides2 + 1)))
            for _ in range(number_of_dice2)
        ]

       # await ctx.send(str(number_of_dice1) + 'd' + str(number_of_sides1))
        await ctx.send(str(number_of_dice1) + 'd' + str(number_of_sides1) + ': ' +', '.join(dice1))
       # await ctx.send(str(number_of_dice2) + 'd' + str(number_of_sides2))
        await ctx.send(str(number_of_dice2) + 'd' + str(number_of_sides2) + ': ' +', '.join(dice2))
        r = 1
        results = '@' + str(dice1[0]) 
        for x in dice1[1:]:
            results = results + '%2' + str(dice1[r]).zfill(2)
            r = r+1
        r = 1
        for x in dice2[1:]:
            results = results + '%2' + str(dice2[r]).zfill(2)
            r = r+1
        await make_request(str(number_of_dice1)+'d'+str(number_of_sides1)+'+'+str(number_of_dice2)+'d'+str(number_of_sides2) +results)
    else:
        roll = roll.split('d')
        number_of_dice = int(roll[0])
        number_of_sides = int(roll[1])
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        #await ctx.send(str(number_of_dice) + 'd' + str(number_of_sides))
        
        await ctx.send(str(number_of_dice) + 'd' + str(number_of_sides) + ': ' + ', '.join(dice))
        r = 1
        results = '@' + str(dice[0]) 
        for x in dice[1:]:
            results = results + '%2' + str(dice[r]).zfill(2)
            r = r+1
        await make_request(str(number_of_dice)+'d'+str(number_of_sides)+results)

       
# run the bot
bot.run('YOUR_DISCORD_BOT_TOKEN')