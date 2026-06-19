import asyncio
import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

class CloseRequestView(discord.ui.View):
    def __init__(self, bot, original_ctx, reason):
        super().__init__(timeout=21600) # 6 Stunden Timeout
        self.bot = bot
        self.original_ctx = original_ctx
        self.reason = reason
        self.message = None

    async def on_timeout(self):
        if self.message:
            await self.message.edit(content="Ticket wurde automatisch geschlossen, da keine Antwort erfolgte.", view=None)
        # Hier die Logik zum Schließen des Tickets einfügen
        await self.close_ticket(self.original_ctx, "Automatisch geschlossen nach 6 Stunden Inaktivität.")

    async def close_ticket(self, ctx, close_reason):
        # Modmail bot specific closing logic
        # This part needs to interact with Modmail's internal closing mechanism.
        # For now, we'll simulate it and log the reason.
        log_channel_id = 123456789012345678 # Placeholder: Replace with actual log channel ID
        log_channel = self.bot.get_channel(log_channel_id)

        if log_channel:
            embed = discord.Embed(title="Ticket geschlossen", description=f"Grund: {close_reason}", color=discord.Color.red())
            embed.add_field(name="Ticket ID", value=ctx.channel.name, inline=False)
            embed.add_field(name="Geschlossen von", value=self.bot.user.display_name, inline=False)
            await log_channel.send(embed=embed)
        
        # Simulate closing the ticket
        await ctx.channel.send(embed=discord.Embed(description=f"Ticket geschlossen. Grund: {close_reason}", color=discord.Color.red()))
        # In a real Modmail plugin, you would call a Modmail API to close the ticket.
        # Example: await self.bot.modmail_api.close_ticket(ctx.channel.id, close_reason)


    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Ticket wird geschlossen.", view=None)
        await self.close_ticket(self.original_ctx, self.reason)
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Ticket bleibt offen.", view=None)
        self.stop()

class FNFsupport(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="closerequest", description="Sendet eine Anfrage zum Schließen des Tickets mit einer Begründung.")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def closerequest(self, ctx: commands.Context, *, reason: str):
        embed = discord.Embed(
            title="Schließanfrage",
            description=f"Bist du bereit, dein Ticket zu schließen? Bitte akzeptiere oder lehne ab.\nGrund: {reason}",
            color=discord.Color.blue()
        )
        view = CloseRequestView(self.bot, ctx, reason)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

async def setup(bot: commands.Bot):
    await bot.add_cog(FNFsupport(bot))
