#!/usr/bin/env python3
"""
MCP SSE Client Example

This example demonstrates how to connect to the MCP server using Server-Sent Events (SSE),
send a tool request, and listen for events.

Usage:
    python mcp_sse_client.py

Requirements:
    - httpx
    - sseclient-py
"""

import httpx
import sseclient
import json
import sys

def main():
    # 1. Connect to /sse and get the session endpoint
    print("Connecting to SSE endpoint...")
    with httpx.stream('GET', 'http://localhost:8000/sse') as response:
        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.event == 'endpoint':
                session_url = 'http://localhost:8000' + event.data
                print(f"Session URL: {session_url}")
                break

    # 2. Send a tool request to /messages/?session_id=...
    payload = {
        "tool_name": "list_dir",
        "parameters": {"directory_path": "."}
    }
    print(f"Sending tool request: {json.dumps(payload, indent=2)}")
    resp = httpx.post(session_url, json=payload)
    print(f"Response status: {resp.status_code}")
    print(f"Response body: {resp.text}")

    # 3. Listen for results on the SSE stream (already open)
    print("Listening for events...")
    for event in client.events():
        print(f"Event: {event.event}")
        print(f"Data: {event.data}")

if __name__ == "__main__":
    main() 