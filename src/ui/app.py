# ABOUTME: Entry point for launching the Gradio web interface
# ABOUTME: Simple launcher that initializes and runs the chat interface

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ui.chat_interface import create_interface


def main():
    """Launch the Gradio web interface."""
    print("=" * 80)
    print("Investment Research Agent - Web Interface")
    print("=" * 80)
    print("\nInitializing Gradio interface...")
    print("Once launched, open the URL shown below in your browser.")
    print("\n" + "=" * 80 + "\n")

    # Create and launch interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,  # Automatically open browser
    )


if __name__ == "__main__":
    main()
