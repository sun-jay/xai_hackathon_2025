#!/usr/bin/env python3
"""
xAI Agentic Tool Calling Script
Simple script to run an xAI agent with a hardcoded prompt
"""

import os
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search, code_execution

# Load environment variables from .env file
load_dotenv()

def main():
    # Initialize the xAI client
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable is not set")

    client = Client(api_key=api_key)

    # Create a chat with agentic tools enabled
    chat = client.chat.create(
        model="grok-4-1-fast",  # reasoning model
        # All server-side tools active
        tools=[
            web_search(),
            x_search(),
            code_execution(),
        ],
    )

    # HARDCODED PROMPT - Change this to your desired question
    PROMPT = "if you call a tool, will the output be cahced and put into the python repl?"

    print(f"Query: {PROMPT}\n")
    print("=" * 80)

    # Add the user prompt to the chat
    chat.append(user(PROMPT))

    # Stream the response and show real-time progress
    is_thinking = True
    for response, chunk in chat.stream():
        # View the server-side tool calls as they are being made in real-time
        for tool_call in chunk.tool_calls:
            print(f"\nCalling tool: {tool_call.function.name}")
            print(f"  Arguments: {tool_call.function.arguments}")

        # Show thinking progress
        if response.usage.reasoning_tokens and is_thinking:
            print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)

        # Print final response
        if chunk.content and is_thinking:
            print("\n\n" + "=" * 80)
            print("Final Response:")
            print("=" * 80)
            is_thinking = False

        if chunk.content and not is_thinking:
            print(chunk.content, end="", flush=True)

    # Print additional information
    print("\n\n" + "=" * 80)
    print("Citations:")
    print("=" * 80)
    for i, citation in enumerate(response.citations, 1):
        print(f"{i}. {citation}")

    print("\n" + "=" * 80)
    print("Usage Statistics:")
    print("=" * 80)
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    print(f"Reasoning tokens: {response.usage.reasoning_tokens}")
    if hasattr(response.usage, 'cached_prompt_text_tokens'):
        print(f"Cached prompt tokens: {response.usage.cached_prompt_text_tokens}")

    print("\n" + "=" * 80)
    print("Server-Side Tool Usage:")
    print("=" * 80)
    print(response.server_side_tool_usage)

    print("\n" + "=" * 80)
    print("All Tool Calls Made:")
    print("=" * 80)
    for i, tool_call in enumerate(response.tool_calls, 1):
        print(f"\n{i}. ID: {tool_call.id}")
        print(f"   Function: {tool_call.function.name}")
        print(f"   Arguments: {tool_call.function.arguments}")


if __name__ == "__main__":
    main()
