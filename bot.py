import discord
from discord.ext import commands
import asyncio
from typing import List, Dict
import traceback

from config import Config
from summarizer import ConversationSummarizer

class ConversationSummarizerBot(commands.Bot):
    """Discord bot for summarizing conversations"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.summarizer = ConversationSummarizer()
        self.message_cache = {}  # Cache for storing recent messages per channel
    
    async def setup_hook(self):
        """Setup hook called when bot starts"""
        print("🤖 Conversation Summarizer Bot is starting up...")
        
        # Test Ollama connection
        print("🔍 Testing Ollama connection...")
        if await self.summarizer.test_connection():
            print(f"✅ Ollama connection successful! Using model: {Config.OLLAMA_MODEL}")
        else:
            print("❌ Ollama connection failed! Make sure Ollama is running with the Mistral model.")
            print("💡 Run: ollama run mistral")
        
        await self.add_cog(SummarizerCommands(self))
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"✅ Bot is ready! Logged in as {self.user}")
        print(f"📊 Serving {len(self.guilds)} guilds")
        print(f"👥 Serving {len(self.users)} users")
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Cache the message for potential summarization
        await self.cache_message(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def cache_message(self, message):
        """Cache recent messages for summarization"""
        channel_id = message.channel.id
        
        if channel_id not in self.message_cache:
            self.message_cache[channel_id] = []
        
        # Add message to cache
        self.message_cache[channel_id].append({
            'author': message.author.display_name,
            'content': message.content,
            'timestamp': message.created_at
        })
        
        # Keep only recent messages (limit to prevent memory issues)
        if len(self.message_cache[channel_id]) > Config.MAX_MESSAGES_TO_SUMMARIZE:
            self.message_cache[channel_id] = self.message_cache[channel_id][-Config.MAX_MESSAGES_TO_SUMMARIZE:]
    
    async def get_recent_messages(self, channel, limit: int = None) -> List[Dict]:
        """Get recent messages from a channel"""
        if limit is None:
            limit = Config.MAX_MESSAGES_TO_SUMMARIZE
        
        messages = []
        async for message in channel.history(limit=limit):
            if not message.author.bot and message.content.strip():
                messages.append({
                    'author': message.author.display_name,
                    'content': message.content,
                    'timestamp': message.created_at
                })
        
        return list(reversed(messages))  # Return in chronological order

class SummarizerCommands(commands.Cog):
    """Commands for conversation summarization"""
    
    def __init__(self, bot: ConversationSummarizerBot):
        self.bot = bot
    
    @commands.command(name='summarize', aliases=['sum', 'summary'])
    async def summarize_conversation(self, ctx, limit: int = 20):
        """
        Summarize recent conversation in the channel
        
        Usage: !summarize [number_of_messages]
        Example: !summarize 30
        """
        try:
            # Send initial response
            loading_msg = await ctx.send("🔄 Analyzing conversation... This may take a moment.")
            
            # Get recent messages
            messages = await self.bot.get_recent_messages(ctx.channel, limit)
            
            if not messages:
                await loading_msg.edit(content="❌ No messages found to summarize.")
                return
            
            # Truncate if too long
            messages = self.bot.summarizer.truncate_conversation(messages)
            
            # Summarize conversation
            summary = await self.bot.summarizer.summarize_conversation(messages)
            
            if summary:
                # Create embed for the summary
                embed = discord.Embed(
                    title="📝 Conversation Summary",
                    description=summary,
                    color=discord.Color.blue(),
                    timestamp=ctx.message.created_at
                )
                
                embed.add_field(
                    name="📊 Analysis Info",
                    value=f"• Messages analyzed: {len(messages)}\n• Channel: {ctx.channel.name}\n• Requested by: {ctx.author.display_name}\n• Model: {Config.OLLAMA_MODEL}",
                    inline=False
                )
                
                embed.set_footer(text="Powered by Ollama Mistral AI")
                
                await loading_msg.edit(content="", embed=embed)
            else:
                await loading_msg.edit(content="❌ Failed to generate summary. Please check if Ollama is running.")
                
        except Exception as e:
            print(f"Error in summarize command: {e}")
            traceback.print_exc()
            await ctx.send("❌ An error occurred while summarizing the conversation.")
    
    @commands.command(name='summarize_cache', aliases=['sumcache'])
    async def summarize_cached(self, ctx):
        """Summarize messages from the bot's cache (faster)"""
        try:
            channel_id = ctx.channel.id
            
            if channel_id not in self.bot.message_cache or not self.bot.message_cache[channel_id]:
                await ctx.send("❌ No cached messages found. Try using `!summarize` instead.")
                return
            
            loading_msg = await ctx.send("🔄 Summarizing cached conversation...")
            
            messages = self.bot.message_cache[channel_id]
            messages = self.bot.summarizer.truncate_conversation(messages)
            
            summary = await self.bot.summarizer.summarize_conversation(messages)
            
            if summary:
                embed = discord.Embed(
                    title="📝 Cached Conversation Summary",
                    description=summary,
                    color=discord.Color.green(),
                    timestamp=ctx.message.created_at
                )
                
                embed.add_field(
                    name="📊 Cache Info",
                    value=f"• Messages analyzed: {len(messages)}\n• Source: Bot cache\n• Requested by: {ctx.author.display_name}\n• Model: {Config.OLLAMA_MODEL}",
                    inline=False
                )
                
                embed.set_footer(text="Powered by Ollama Mistral AI")
                
                await loading_msg.edit(content="", embed=embed)
            else:
                await loading_msg.edit(content="❌ Failed to generate summary from cache.")
                
        except Exception as e:
            print(f"Error in summarize_cache command: {e}")
            await ctx.send("❌ An error occurred while summarizing cached conversation.")
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 Conversation Summarizer Bot",
            description="A Discord bot that uses Ollama Mistral AI to summarize conversations and arguments.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Commands",
            value="""
**!summarize [number]** - Summarize recent messages in the channel
**!summarize_cache** - Summarize messages from bot's cache (faster)
**!help** - Show this help message

**Examples:**
`!summarize 30` - Summarize the last 30 messages
`!summarize` - Summarize the last 20 messages (default)
`!sumcache` - Summarize cached messages
            """,
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Features",
            value="""
• Local AI-powered conversation summarization
• Intelligent message filtering
• Automatic conversation caching
• Configurable message limits
• Rich embed responses
• Powered by Ollama Mistral
            """,
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ using Ollama Mistral")
        
        await ctx.send(embed=embed)

async def main():
    """Main function to run the bot"""
    try:
        # Validate configuration
        Config.validate()
        
        # Create and run bot
        bot = ConversationSummarizerBot()
        await bot.start(Config.DISCORD_TOKEN)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 