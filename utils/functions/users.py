# Discord
from discord.ext.commands import command, cooldown, BucketType, Cog
from discord import Member, Message, User, TextChannel

import utils

from asyncio import sleep
from random import randint, choice
from math import floor

class UserFunctions(object):
    bot = None

    @property  #+ The Gem Logs
    def gem_log(cls):
        return cls.bot.get_channel(cls.bot.config['logs']['gem'])

    # For level ups!
    @classmethod
    async def level_up(cls, user:Member, channel:TextChannel=None):
        '''Checks if they should level up and then levels then up!'''

        #? Set Varibles
        lvl = utils.Levels.get(user.id)
        g = utils.Gems.get(user.id)

        #? Check if they should even level up!
        requiredexp = await cls.determine_required_exp(lvl.level)
        if lvl.exp < requiredexp:
            return

        #+ Level em the hell up!
        lvl.exp = 0
        lvl.level += 1
        g.emerald += (lvl.level*500)
        async with cls.bot.database() as db:
            await lvl.save(db)
            await g.save(db)

        await cls.check_level(user=user)

        #? Log it and tell em.
        if channel:
            msg = await channel.send(f"🎉 {user.mention} is now level: **{lvl.level:,}\n**Granting them: **{round(amount):,}x** {coin}")

        await cls.gem_log.send(f"**{user.name}** leveled up and is now level **{lvl.level:,}**\nGranting them: **{round(amount):,}x** {coin}")

        await sleep(6)
        try: await msg.delete()
        except: pass



    @classmethod
    async def determine_required_exp(cls, level:int):
        """Determines how much exp is needed to level up!"""
        if level == 0:
            requiredexp = 10
        elif level < 5:
            requiredexp = level*25
        else:
            requiredexp = round(level**2.75)
        return requiredexp


    @classmethod
    async def check_level(cls, user:Member):
        """Checks the highest level role that the given user is able to receive"""

        # Get the users
        guild = cls.bot.get_guild(cls.bot.config['garden_id'])
        lvl = utils.Levels.get(user.id)

        level_roles = {
            100: "Ancient Serpent Deceiver (Lvl 100)",
            90: "Leviathan (Lvl 90)",
            80: "Cosmic Horror (Lvl 80)",
            70: "Dragon (Lvl 70)",
            65: "Malevolent One (Lvl 65)",
            60: "Oath Taker (Lvl 60)",
            55: "Shadow Priest (Lvl 55)",
            50: "Warlock (Lvl 50)",
            45: "Sorcerer (Lvl 45)",
            40: "Cleric (Lvl 40)",
            35: "Paladin (Lvl 35)",
            30: "Adventurer (Lvl 30)",
            25: "Warrior (Lvl 25)",
            20: "Hunter (Lvl 20)",
            15: "Villager (Lvl 15)",
            10: "Beggar (Lvl 10)",
            5: "Nit-Wit (Lvl 5)",
            0: "Sacrifice (Lvl 1)",
        }

        # Get roles from the user we'd need to delete
        try:
            role_to_delete = [i for i in user.roles if i.name in level_roles.values()]
        except IndexError:
            role_to_delete = None

        # Get role that the user is viable to have
        viable_level_roles = {i:o for i, o in level_roles.items() if lvl.level >= i}
        if viable_level_roles:
            role_to_add = viable_level_roles[max(viable_level_roles.keys())]
        else:
            role_to_add = None

        # Add the roles
        if role_to_delete:
            await user.remove_roles(*role_to_delete, reason="Removing Level Role.")

        if role_to_add:
            try:
                role = utils.DiscordGet(guild.roles, name=role_to_add)
                await user.add_roles(role, reason="Adding Level Role.")
            except: 
                print(f'Failed to apply level role: {user.name} getting role: {role_to_add}'