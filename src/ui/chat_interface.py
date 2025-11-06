# ABOUTME: Gradio web interface for the investment research agent
# ABOUTME: Features chat, source citations, tool call visibility, and conversation management

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

import gradio as gr
from dotenv import load_dotenv

from src.agent.research_agent import ResearchAgent

load_dotenv()


class ChatInterface:
    """Gradio chat interface for the investment research agent."""

    def __init__(self):
        """Initialize the chat interface."""
        self.agent = None
        self.tool_calls_log: List[str] = []

    def initialize_agent(self) -> str:
        """Initialize the research agent and return status message."""
        try:
            self.agent = ResearchAgent()
            return "✅ Agent initialized successfully!"
        except Exception as e:
            return f"❌ Error initializing agent: {str(e)}"

    def chat(
        self,
        message: str,
        history: List[List[str]],
    ) -> Tuple[List[List[str]], str]:
        """
        Handle chat messages and return updated history and citations.

        Args:
            message: User's message
            history: Chat history as list of [user_msg, agent_msg] pairs

        Returns:
            Tuple of (updated_history, citations_text)
        """
        if not self.agent:
            self.initialize_agent()

        try:
            # Track tool calls
            original_messages_count = len(self.agent.messages)

            # Get response from agent
            response = self.agent.chat(message)

            # Extract tool calls from new messages
            new_messages = self.agent.messages[original_messages_count:]
            citations = self._extract_citations(new_messages)

            # Add to history
            history.append([message, response])

            return history, citations

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            history.append([message, error_msg])
            return history, ""

    def _extract_citations(self, messages: List[Dict[str, Any]]) -> str:
        """
        Extract citations and tool calls from messages.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted citations text
        """
        citations_parts = []

        for msg in messages:
            # Check for tool responses
            if msg.get("role") == "tool" and msg.get("name") == "search_investment_research":
                content = msg.get("content", "")

                # Extract sources from the RAG response
                if "## Excerpt" in content:
                    # Parse the excerpts
                    excerpts = content.split("## Excerpt")[1:]  # Skip header
                    citations_parts.append("### 📚 Research Sources\n")

                    for excerpt in excerpts:
                        # Extract source info
                        if "**Source:**" in excerpt:
                            lines = excerpt.split("\n")
                            for line in lines:
                                if "**Source:**" in line:
                                    source = line.replace("**Source:**", "").strip()
                                    citations_parts.append(f"- {source}")
                                elif "**Relevance Score:**" in line:
                                    score = line.replace("**Relevance Score:**", "").strip()
                                    citations_parts.append(f"  Relevance: {score}")
                                    break

            # Track tool calls for debugging
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments
                    self.tool_calls_log.append(f"🔧 {tool_name}({tool_args})")

        if citations_parts:
            return "\n".join(citations_parts)
        else:
            return "No sources cited in this response."

    def clear_conversation(self) -> Tuple[List, str, str]:
        """
        Clear the conversation history.

        Returns:
            Tuple of (empty_history, empty_citations, status_message)
        """
        if self.agent:
            self.agent.clear_history()
        self.tool_calls_log = []
        return [], "", "🗑️ Conversation cleared"

    def export_conversation(self) -> str:
        """
        Export conversation to JSON file.

        Returns:
            Status message with filepath
        """
        if not self.agent:
            return "❌ No conversation to export"

        try:
            filepath = f"conversation_export_{len(self.agent.messages)}.json"
            self.agent.export_conversation(filepath)
            return f"💾 Conversation exported to: {filepath}"
        except Exception as e:
            return f"❌ Export failed: {str(e)}"

    def get_tool_calls_log(self) -> str:
        """Get the tool calls log for debugging."""
        if not self.tool_calls_log:
            return "No tool calls yet."
        return "\n".join(self.tool_calls_log)


def create_interface() -> gr.Blocks:
    """
    Create the Gradio interface.

    Returns:
        Gradio Blocks interface
    """
    chat_interface = ChatInterface()

    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px;
        margin: auto;
    }
    .chat-container {
        height: 600px;
    }
    .citations-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    """

    with gr.Blocks(
        title="Investment Research Agent",
        theme=gr.themes.Soft(),
        css=custom_css,
    ) as interface:
        # Header
        gr.Markdown(
            """
            # 💼 Investment Research Agent

            Ask questions about market outlook, asset allocation, and investment strategy
            based on UBS House View reports and SEC filings.

            **Examples:**
            - What is UBS's view on US equities?
            - What are the key risks to the market outlook?
            - What is the outlook for interest rates?
            - What sectors does UBS recommend?
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_copy_button=True,
                    elem_classes=["chat-container"],
                )

                with gr.Row():
                    msg_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Type your investment research question here...",
                        scale=4,
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)

                with gr.Row():
                    clear_btn = gr.Button("Clear Conversation", size="sm")
                    export_btn = gr.Button("Export Conversation", size="sm")

                # Status messages
                status_output = gr.Textbox(label="Status", interactive=False, visible=False)

            with gr.Column(scale=1):
                # Citations panel
                gr.Markdown("### 📚 Sources & Citations")
                citations_output = gr.Textbox(
                    label="Research Sources",
                    lines=15,
                    interactive=False,
                    elem_classes=["citations-box"],
                    placeholder="Sources will appear here after each query...",
                )

                # Tool calls debugging panel (collapsible)
                with gr.Accordion("🔧 Tool Calls (Debug)", open=False):
                    tool_calls_output = gr.Textbox(
                        label="Function Calls Log",
                        lines=10,
                        interactive=False,
                        placeholder="Tool calls will be logged here...",
                    )
                    refresh_tools_btn = gr.Button("Refresh Tool Log", size="sm")

        # Initialize agent on load
        interface.load(
            chat_interface.initialize_agent,
            outputs=[status_output],
        )

        # Wire up chat functionality
        def submit_message(message, history):
            """Submit message and update both chat and citations."""
            new_history, citations = chat_interface.chat(message, history)
            return new_history, citations, ""

        # Submit on button click
        submit_btn.click(
            submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, citations_output, msg_input],
        )

        # Submit on Enter key
        msg_input.submit(
            submit_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, citations_output, msg_input],
        )

        # Clear conversation
        clear_btn.click(
            chat_interface.clear_conversation,
            outputs=[chatbot, citations_output, status_output],
        )

        # Export conversation
        export_btn.click(
            chat_interface.export_conversation,
            outputs=[status_output],
        ).then(
            lambda: gr.update(visible=True),
            outputs=[status_output],
        )

        # Refresh tool calls log
        refresh_tools_btn.click(
            chat_interface.get_tool_calls_log,
            outputs=[tool_calls_output],
        )

        # Footer
        gr.Markdown(
            """
            ---
            **Note:** This agent provides information based on research reports and should not be considered
            personalized investment advice. Consult with a licensed financial advisor before making investment decisions.

            **Data Sources:** UBS House View Reports (2024-2025), SEC 10-K Filings
            """
        )

    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
