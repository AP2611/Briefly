import ollama
import asyncio
from typing import List, Dict, Optional
from config import Config

class ConversationSummarizer:
    """Handles conversation summarization using Ollama with Mistral"""
    
    def __init__(self):
        """Initialize the summarizer with Ollama client"""
        self.client = ollama.Client(host=Config.OLLAMA_HOST)
        self.model = Config.OLLAMA_MODEL
    
    async def summarize_conversation(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Summarize a list of messages using Ollama with Mistral
        
        Args:
            messages: List of message dictionaries with 'author' and 'content' keys
            
        Returns:
            Summarized conversation as a string, or None if summarization fails
        """
        if not messages:
            return "No messages to summarize."
        
        try:
            # Format messages for the model
            conversation_text = self._format_conversation(messages)
            
            # Create the prompt for summarization
            prompt = self._create_summarization_prompt(conversation_text)
            
            # Call Ollama API
            response = await self._call_ollama(prompt)
            
            if response and response.strip():
                return response.strip()
            else:
                return None
            
        except Exception as e:
            print(f"Error during summarization: {e}")
            return None
    
    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Make async call to Ollama API"""
        try:
            # Run Ollama call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._sync_ollama_call, 
                prompt
            )
            return response
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    def _sync_ollama_call(self, prompt: str) -> Optional[str]:
        """Synchronous call to Ollama API"""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes conversations. Provide clear, concise summaries that capture the main points and key arguments."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": Config.TEMPERATURE,
                    "num_predict": Config.MAX_TOKENS
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            print(f"Error in Ollama call: {e}")
            return None
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation messages into a readable text format"""
        formatted_messages = []
        
        for msg in messages:
            author = msg.get('author', 'Unknown')
            content = msg.get('content', '').strip()
            
            if content:  # Only include non-empty messages
                formatted_messages.append(f"{author}: {content}")
        
        return "\n".join(formatted_messages)
    
    def _create_summarization_prompt(self, conversation_text: str) -> str:
        """Create a prompt for the AI to summarize the conversation"""
        return f"""
Please provide a concise summary of the following conversation. Focus on:
- The main topic or subject being discussed
- Key points and arguments made by participants
- Any conclusions or decisions reached
- The overall tone and nature of the discussion

Conversation:
{conversation_text}

Please provide a clear, well-structured summary in 2-3 sentences.
"""
    
    def truncate_conversation(self, messages: List[Dict[str, str]], max_length: int = None) -> List[Dict[str, str]]:
        """
        Truncate conversation to fit within token limits
        
        Args:
            messages: List of message dictionaries
            max_length: Maximum number of characters to include
            
        Returns:
            Truncated list of messages
        """
        if max_length is None:
            max_length = Config.MAX_MESSAGE_LENGTH
        
        truncated_messages = []
        current_length = 0
        
        # Start from the most recent messages and work backwards
        for msg in reversed(messages):
            msg_content = f"{msg.get('author', '')}: {msg.get('content', '')}\n"
            msg_length = len(msg_content)
            
            if current_length + msg_length <= max_length:
                truncated_messages.insert(0, msg)
                current_length += msg_length
            else:
                break
        
        return truncated_messages
    
    async def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            # Try to list models to test connection
            loop = asyncio.get_event_loop()
            models = await loop.run_in_executor(None, self.client.list)
            return True
        except Exception as e:
            print(f"Ollama connection test failed: {e}")
            return False 