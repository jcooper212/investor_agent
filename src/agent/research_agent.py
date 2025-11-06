# ABOUTME: Investment research agent using OpenAI function calling with RAG
# ABOUTME: Handles multi-turn conversations about market outlook and investment strategy

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from openai import OpenAI

from src.tools.rag_retrieval import create_rag_tool_function
from src.rag.vector_store import VectorStore

load_dotenv()


class ResearchAgent:
    """
    Investment research agent that uses RAG to answer questions about
    market outlook, asset allocation, and investment strategy from UBS House View reports.
    """

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        vector_store: Optional[VectorStore] = None,
    ):
        """
        Initialize the research agent.

        Args:
            model: OpenAI model to use (default: gpt-4-turbo-preview)
            vector_store: Optional existing VectorStore instance
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

        # Initialize RAG tool
        self.vector_store = vector_store or VectorStore()
        self.rag_tool = create_rag_tool_function(self.vector_store)

        # Conversation history
        self.messages: List[Dict[str, Any]] = []

        # System prompt
        self.system_prompt = self._create_system_prompt()
        self.messages.append({"role": "system", "content": self.system_prompt})

        # Define tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_investment_research",
                    "description": (
                        "Search UBS House View reports and SEC filings for investment research insights. "
                        "Use this when you need information about market outlook, asset allocation, "
                        "sector analysis, risk factors, Fed policy, or investment recommendations."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": (
                                    "The investment research question or topic to search for. "
                                    "Examples: 'What is UBS view on US equities?', "
                                    "'What are key risks to the market?', "
                                    "'What is the outlook for interest rates?'"
                                ),
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Number of relevant excerpts to return (default: 5)",
                                "default": 5,
                            },
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

        print("✅ Research Agent initialized")
        print(f"   Model: {self.model}")
        print(f"   Vector store: {self.vector_store.get_collection_stats()['count']} documents")

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the research agent."""
        return """You are an expert investment research assistant with access to UBS House View reports and SEC filings.

Your role is to help users understand:
- Market outlook and economic conditions
- Asset allocation recommendations
- Sector analysis and investment themes
- Risk factors and market uncertainties
- Investment strategy and portfolio positioning
- Regional market views (US, Europe, Asia, Emerging Markets)
- Fed policy and interest rate outlook

IMPORTANT GUIDELINES:
1. **Use the search_investment_research tool** to find information from research reports. Always search for relevant data before answering.

2. **Cite your sources** - When providing information, cite the specific report and page number. For example: "According to UBS House View March 2025 (Page 5)..."

3. **Be objective** - Present the research findings as they are. Don't add personal opinions or predictions.

4. **Disclaimers** - When providing investment advice or recommendations, include:
   "This information is based on research reports and should not be considered personalized investment advice. Consult with a licensed financial advisor before making investment decisions."

5. **Acknowledge limitations** - If information is not available in the research database, say so clearly. Don't make up information.

6. **Multi-turn context** - Remember previous questions in the conversation and build on them naturally.

7. **Be conversational** - Provide helpful, clear answers while maintaining a professional tone.

Your goal is to make investment research accessible and useful while maintaining accuracy and proper attribution."""

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.

        Args:
            user_message: The user's question or message

        Returns:
            The agent's response string
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})

        try:
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
            )

            response_message = response.choices[0].message

            # Handle tool calls
            while response_message.tool_calls:
                # Add assistant's response with tool calls to history
                self.messages.append(response_message)

                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"🔍 Tool call: {function_name}({json.dumps(function_args, indent=2)})")

                    # Execute the function
                    if function_name == "search_investment_research":
                        function_response = self.rag_tool(**function_args)
                    else:
                        function_response = json.dumps({"error": f"Unknown function: {function_name}"})

                    # Add function response to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response,
                    })

                # Get next response
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tools,
                    tool_choice="auto",
                )
                response_message = response.choices[0].message

            # Add final response to history
            assistant_message = response_message.content
            self.messages.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def clear_history(self, keep_system_prompt: bool = True):
        """
        Clear conversation history.

        Args:
            keep_system_prompt: If True, keeps the system prompt (default: True)
        """
        if keep_system_prompt:
            self.messages = [{"role": "system", "content": self.system_prompt}]
        else:
            self.messages = []
        print("🗑️  Conversation history cleared")

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.messages.copy()

    def export_conversation(self, filepath: str):
        """
        Export conversation history to a JSON file.

        Args:
            filepath: Path to save the conversation
        """
        with open(filepath, "w") as f:
            json.dump(self.messages, f, indent=2)
        print(f"💾 Conversation exported to: {filepath}")


def main():
    """CLI interface for testing the research agent."""
    print("=" * 80)
    print("Investment Research Agent - CLI Interface")
    print("=" * 80)
    print("\nCommands:")
    print("  - Type your question and press Enter")
    print("  - Type 'clear' to reset conversation")
    print("  - Type 'history' to see conversation history")
    print("  - Type 'export' to save conversation to JSON")
    print("  - Type 'quit' or 'exit' to end session")
    print("\n" + "=" * 80 + "\n")

    # Initialize agent
    agent = ResearchAgent()

    while True:
        try:
            # Get user input
            user_input = input("\n🔵 You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["quit", "exit"]:
                print("\n👋 Goodbye!")
                break

            elif user_input.lower() == "clear":
                agent.clear_history()
                continue

            elif user_input.lower() == "history":
                history = agent.get_history()
                print(f"\n📜 Conversation History ({len(history)} messages):")
                for i, msg in enumerate(history):
                    role = msg["role"]
                    content = msg.get("content", "[tool call]")
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"   {i+1}. [{role}] {content}")
                continue

            elif user_input.lower() == "export":
                filepath = f"conversation_{len(agent.messages)}.json"
                agent.export_conversation(filepath)
                continue

            # Get response from agent
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
