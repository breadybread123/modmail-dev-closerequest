import asyncio
import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

class CloseRequestView(discord.ui.View):
    def __init__(self, bot, original_ctx, reason, recipient):
        super().__init__(timeout=21600) # 6 hours timeout
        self.bot = bot
        self.original_ctx = original_ctx
        self.reason = reason
        self.recipient = recipient # The user who opened the ticket
        self.message = None # This will be the message sent to the recipient
        self.log_channel_id = 1445473996081725460 # User provided log channel ID

    async def on_timeout(self):
        # This only runs if the 6 hours pass without interaction
        if self.message:
            await self.message.edit(content="Your ticket was automatically closed due to inactivity.", view=None)
        await self._close_modmail_thread(self.original_ctx, "Automatically closed after 6 hours of inactivity.")

    async def _close_modmail_thread(self, ctx, close_reason):
        try:
            # Send log to the specified log channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if log_channel:
                log_embed = discord.Embed(title="Ticket Closed", description=f"Reason: {close_reason}", color=discord.Color.red())
                log_embed.add_field(name="Ticket ID", value=ctx.channel.name, inline=False)
                log_embed.add_field(name="Closed by", value=self.bot.user.display_name, inline=False)
                await log_channel.send(embed=log_embed)

            # Send closing message to the user who opened the ticket (via DM)
            user_embed = discord.Embed(description=f"Your ticket has been closed. Reason: {close_reason}", color=discord.Color.red())
            await self.recipient.send(embed=user_embed)

            # Attempt to close the thread using Modmail's internal mechanism
            if hasattr(ctx, 'thread') and hasattr(ctx.thread, 'close'):
                await ctx.thread.close(closer=self.bot.user, silent=False, delete_channel=True, message=close_reason)
            elif hasattr(self.bot, 'modmail') and hasattr(self.bot.modmail, 'close_thread'):
                await self.bot.modmail.close_thread(ctx.channel.id, closer=self.bot.user, reason=close_reason)
            else:
                await ctx.channel.send(embed=discord.Embed(description="Could not programmatically close the Modmail thread. Please close it manually.", color=discord.Color.orange()))

        except Exception as e:
            print(f"Error closing Modmail thread: {e}")
            await ctx.channel.send(embed=discord.Embed(description=f"An error occurred while trying to close the ticket: {e}", color=discord.Color.red()))

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Stop the view (and thus the timeout timer) immediately
        self.stop()
        await interaction.response.edit_message(content="Ticket is being closed.", view=None)
        await self._close_modmail_thread(self.original_ctx, self.reason)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Stop the view (and thus the timeout timer) immediately
        self.stop()
        await interaction.response.edit_message(content="Ticket remains open.", view=None)
        
        # Send a message to the staff channel that the close request was denied
        staff_denied_embed = discord.Embed(
            title="Close Request Denied",
            description=f"The close request for this ticket was denied by {self.recipient.display_name} (ID: {self.recipient.id}). The ticket remains open.",
            color=discord.Color.orange()
        )
        await self.original_ctx.send(embed=staff_denied_embed)

class CloseRequest(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="closerequest", description="Sends a request to close the ticket with a reason.")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def closerequest(self, ctx: commands.Context, *, reason: str):
        if not hasattr(ctx, 'thread') or not hasattr(ctx.thread, 'recipient'):
            await ctx.send(embed=discord.Embed(description="Could not find the ticket recipient. Cannot send close request.", color=discord.Color.red()))
            return

        recipient = ctx.thread.recipient

        user_embed = discord.Embed(
            title="Close Request",
            description=f"Are you ready for your ticket to be closed? Please accept or decline.\nReason: {reason}",
            color=discord.Color.blue()
        )
        view = CloseRequestView(self.bot, ctx, reason, recipient)
        try:
            dm_message = await recipient.send(embed=user_embed, view=view)
            view.message = dm_message
            
            staff_embed = discord.Embed(
                title="Close Request Sent",
                description=f"Close request for this ticket has been sent to {recipient.display_name} (ID: {recipient.id}).\nReason: {reason}",
                color=discord.Color.green()
            )
            await ctx.send(embed=staff_embed)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description=f"Could not send DM to {recipient.display_name}. User might have DMs disabled.", color=discord.Color.red()))

async def setup(bot: commands.Bot):
    await bot.add_cog(CloseRequest(bot))
