# -*- coding: utf-8 -*-
"""
[File: function_real.py]
[Author: Jules (AI Agent)]
[Date: 2025-08-23]

[Summary]
This module handles real-time data reception and processing via the Upbit WebSocket API.
It uses an asynchronous approach (asyncio) to receive real-time ticker data and
updates the UI with the relevant information.

[Global Variables]
- None.

[Dependencies & Interconnections]

[Incoming Calls (External modules calling this module)]
- `Main.py` -> `web_socket_initial()`: Called as an asyncio task at program startup to run the WebSocket loop.

[Outgoing Calls (This module calling external modules)]
- None. (Only calls external libraries like `websockets`, etc.)

[Global Variable Access]
- `on_message()` -> `function_complex.avg_price` (READ): Reads the `avg_price` variable from the `function_complex` module
  to calculate the real-time profit/loss percentage against the current price.

[Note]
The `web_socket_initial` function includes a `while True` loop that attempts to
automatically reconnect after 5 seconds if the WebSocket connection is dropped.
"""

# Import necessary libraries
import jwt          # PyJWT for creating and validating JWT tokens
import uuid         # For generating unique identifiers
import websockets   # Asynchronous WebSocket client
import os           # For accessing environment variables
import json         # For parsing JSON data
import function_complex # To access variables from other modules (avg_price)
import asyncio      # For the sleep function in the reconnect logic

# Main asynchronous function to connect to the Upbit WebSocket and receive real-time data
async def web_socket_initial(ui):
    """
    Connects to the Upbit WebSocket server to receive real-time ticker data and update the UI.
    - Creates a JWT token for authentication.
    - Sends a subscription message for a specific ticker upon successful connection.
    - Parses received messages and updates a text browser in the UI.
    - ui: The PySide6 UI object to be updated.
    """

    # Internal async function to be called upon receiving a WebSocket message
    async def on_message(ws):
        """
        Continuously receives and processes messages from the server.
        """
        async for message in ws:
            # Decode the received message (bytes) into a UTF-8 string
            data = message.decode('utf-8')
            # Parse the JSON formatted string into a Python dictionary
            json_data = json.loads(data)
            # Extract the 'trade_price' (current price)
            trade_price = json_data.get("trade_price", "N/A")

            # Get the global 'avg_price' (average buy price) from the function_complex module
            avg_price = function_complex.avg_price

            # Calculate the percentage difference between the current price and the average buy price
            price_difference_percentage = 0
            if avg_price != 0 and trade_price != "N/A":
                try:
                    price_difference_percentage = round((float(trade_price) - float(avg_price)) / float(avg_price) * 100, 3)
                except ValueError:
                    price_difference_percentage = 0 # Handle cases where price is not a number

            # Display the current price, average buy price, and percentage difference in the UI's textBrowser_4
            ui.textBrowser_4.setText(f"{str(trade_price)} / {avg_price} / {price_difference_percentage}%")

    # Internal async function to be called upon successful WebSocket connection
    async def on_connect(ws):
        """
        Sends a subscription message and logs the status to the UI upon successful connection.
        """
        log_message = "[INFO] Connected to real-time ticker server."
        print(log_message)
        ui.textBrowser_2.append(log_message)
        # Create a subscription message in JSON format and send it to the server
        # ticket: unique identifier, type: subscription type (ticker), codes: list of tickers
        await ws.send('[{"ticket":"UNIQUE_TICKET"},{"type":"ticker", "codes":["KRW-XRP"], "isOnlyRealtime" : "True"}]')

    # Internal async function to be called when a WebSocket error occurs
    async def on_error(ws, err):
        """
        Called when a WebSocket communication error occurs. Logs the error to the UI.
        """
        log_message = f"[ERROR] Real-time ticker server error: {err}"
        print(log_message)
        ui.textBrowser_2.append(log_message)

    # Internal async function to be called when the WebSocket connection is closed
    async def on_close(ws, code, reason):
        """
        Called when the WebSocket connection is closed. Logs the status to the UI.
        """
        log_message = f"[INFO] Real-time ticker server connection closed. Code: {code}, Reason: {reason}"
        print(log_message)
        ui.textBrowser_2.append(log_message)

    # Create JWT token for WebSocket authentication
    access_key = os.environ.get('UPBIT_OPEN_API_ACCESS_KEY')
    secret_key = os.environ.get('UPBIT_OPEN_API_SECRET_KEY')

    # Terminate the function if keys are not found
    if not access_key or not secret_key:
        print("API keys are not set in environment variables.")
        return

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization_token = f'Bearer {jwt_token}'
    headers = {"Authorization": authorization_token}

    # Upbit WebSocket server address
    uri = "wss://api.upbit.com/websocket/v1"

    # Connect to the WebSocket server and start communication
    while True: # Use a while loop for reconnection logic
        try:
            async with websockets.connect(uri, extra_headers=headers) as ws:
                await on_connect(ws)
                await on_message(ws)
        except websockets.exceptions.ConnectionClosed as e:
            # Log only if the connection closure was not normal
            if not e.code == 1000:
                log_message = f"[ERROR] WebSocket connection closed unexpectedly: {e}"
                print(log_message)
                ui.textBrowser_2.append(log_message)
            await on_close(ws, e.code, e.reason)
        except Exception as e:
            log_message = f"[ERROR] An exception occurred during WebSocket processing: {e}"
            print(log_message)
            ui.textBrowser_2.append(log_message)

        # Wait a moment before attempting to reconnect
        reconnect_message = "[INFO] Attempting to reconnect to the real-time server in 5 seconds..."
        print(reconnect_message)
        ui.textBrowser_2.append(reconnect_message)
        await asyncio.sleep(5)