# -*- coding: utf-8 -*-
"""
[File: function.py]
[Author: Jules (AI Agent)]
[Date: 2025-08-23]

[Summary]
This module handles all low-level communication with the Upbit REST API.
It includes core functions for API requests, response handling, and authentication
header generation for direct communication with the Upbit server.

[Global Variables]
- `feature_data` (pd.DataFrame): Stores technical indicator settings loaded via the `file_load3` function. (Not directly used by other functions at the moment).

[Dependencies & Interconnections]

[Incoming Calls (External modules calling this module)]
- `Main.py` -> `file_load()`: To load API keys.
- `Main.py` -> `open_order()`: To execute a buy order.
- `function_complex.py` -> `hold_account()`: To get account balance.
- `function_complex.py` -> `order_wait_history()`: To get open orders.
- `function_complex.py` -> `order_close_history()`: To get closed/cancelled orders.
- `function_complex.py` -> `hoga_list()`: To get order book data.
- `function_complex.py` -> `candle()`: To get candle data.
- `function_complex.py` -> `open_order()`: To execute a market sell (liquidation) order.
- `function_complex.py` -> `close_order()`: To cancel an open order.
- `function_complex.py` -> `file_load2()`: To load local historical candle data.

[Outgoing Calls (This module calling external modules)]
- None. (Only calls external libraries like `requests`, `jwt`, etc.)

[Global Variable Access]
- None.
"""

# Import necessary libraries
import pandas as pd
import jwt
import hashlib
import os
import requests
import uuid
import json
from urllib.parse import urlencode, unquote, quote

# Global DataFrame to store technical indicator settings
feature_data = pd.DataFrame()

# Function to load API key settings file
def file_load(path):
    """
    Reads Access Key and Secret Key from a CSV file at the specified path and sets them as environment variables.
    Also sets the Upbit API server URL as an environment variable.
    - path: Path to the settings file.
    """
    try:
        data = pd.read_csv(path)
        Access_Key = data.loc[data['type'] == 'Access_Key', 'value'].values[0]
        Secret_Key = data.loc[data['type'] == 'Secret_Key', 'value'].values[0]
        os.environ['UPBIT_OPEN_API_ACCESS_KEY'] = Access_Key
        os.environ['UPBIT_OPEN_API_SECRET_KEY'] = Secret_Key
        os.environ['UPBIT_OPEN_API_SERVER_URL'] = 'https://api.upbit.com'
    except FileNotFoundError:
        print(f"[ERROR] Settings file not found: {path}")
    except Exception as e:
        print(f"[ERROR] Error loading settings file: {e}")

# Function to load a general CSV file
def file_load2(path):
    """
    Reads a CSV file from the specified path and returns it as a DataFrame (mainly for historical data).
    - path: Path to the data file.
    """
    try:
        data = pd.read_csv(path)
        return data
    except FileNotFoundError:
        print(f"[ERROR] Data file not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] Error loading data file: {e}")
        return pd.DataFrame()

# Function to load technical indicator settings
def file_load3(path):
    """
    Reads technical indicator settings from a CSV file at the specified path and stores them in the global `feature_data` DataFrame.
    - path: Path to the technical indicator settings file.
    """
    global feature_data
    try:
        data = pd.read_csv(path)
        feature_data = pd.DataFrame(data)
    except FileNotFoundError:
        print(f"[ERROR] Indicator settings file not found: {path}")
    except Exception as e:
        print(f"[ERROR] Error loading indicator settings file: {e}")

# Function to get order book information for a specific ticker
def hoga_list(ticker):
    """
    Fetches the current order book for a specific ticker from the Upbit API and returns it as a DataFrame.
    - ticker: The ticker to query (e.g., "KRW-XRP").
    """
    url = f"https://api.upbit.com/v1/orderbook?markets={ticker}&level=0"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        data = response.json()
        orderbook_units = data[0]['orderbook_units']
        df = pd.DataFrame(orderbook_units, columns=['ask_price', 'bid_price'])
        return df
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] Failed to fetch order book: {e}")
        return pd.DataFrame()
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[API ERROR] Failed to parse order book data: {e}")
        return pd.DataFrame()

# Function to get information on all available markets
def Market_Data():
    """
    Fetches information on all available markets from the Upbit API.
    - GET /v1/market/all
    """
    url = "https://api.upbit.com/v1/market/all"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] Failed to fetch all market data: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"[API ERROR] Failed to parse all market data: {e}")
        return pd.DataFrame()

# Function to get current ticker information for a specific market
def Market_Data_Specific(ticker):
    """
    Fetches the current Ticker information for a specific market from the Upbit API.
    - GET /v1/ticker
    - ticker: The ticker to query (e.g., "KRW-XRP").
    """
    url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] Failed to fetch specific market ({ticker}) data: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"[API ERROR] Failed to parse specific market ({ticker}) data: {e}")
        return pd.DataFrame()

# Function to fetch minute candle data
def candle(type, ticker, count, time):
    """
    Fetches minute candle data for a specific ticker from the Upbit API (max 200 candles).
    - GET /v1/candles/minutes/{unit}
    """
    if time == 0:
        url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&count={count}"
    else:
        encoded_time = quote(time)
        url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&to={encoded_time}&count={count}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] Failed to fetch candle data: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"[API ERROR] Failed to parse candle data: {e}")
        return pd.DataFrame()

# Common function to generate authentication headers for API requests
def _get_auth_headers(query_params=None):
    """
    Creates JWT headers for authentication.
    - query_params: If query parameters exist, they are passed for hashing.
    """
    access_key = os.environ.get('UPBIT_OPEN_API_ACCESS_KEY')
    secret_key = os.environ.get('UPBIT_OPEN_API_SECRET_KEY')
    if not access_key or not secret_key:
        raise ValueError("API keys are not set in environment variables.")

    payload = {'access_key': access_key, 'nonce': str(uuid.uuid4())}

    if query_params:
        query_string = unquote(urlencode(query_params, doseq=True)).encode("utf-8")
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()
        payload['query_hash'] = query_hash
        payload['query_hash_alg'] = 'SHA512'

    jwt_token = jwt.encode(payload, secret_key)
    return {'Authorization': f'Bearer {jwt_token}'}

# Function to get the full account balance
def hold_account():
    """
    Fetches information on all assets currently held in the account from the Upbit API (authentication required).
    - GET /v1/accounts
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    try:
        headers = _get_auth_headers()
        response = requests.get(server_url + '/v1/accounts', headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] Failed to fetch account balance: {e}")
        return pd.DataFrame()

# Function to get order chance information
def order_possible(ticker):
    """
    Fetches order chance information for a specific market from the Upbit API (authentication required).
    - GET /v1/orders/chance
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker}
    try:
        headers = _get_auth_headers(params)
        response = requests.get(server_url + '/v1/orders/chance', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] Failed to fetch order chance info: {e}")
        return pd.DataFrame()

# Function to place an order
def open_order(ticker, type, ord_type, volume, price, ui):
    """
    Places a limit or market order via the Upbit API (authentication required).
    - POST /v1/orders
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'side': type, 'ord_type': ord_type}

    if ord_type == 'price': # Market buy
        params['price'] = price
    elif ord_type == 'market': # Market sell
        params['volume'] = volume
    else: # Limit order
        params['volume'] = volume
        params['price'] = price

    try:
        headers = _get_auth_headers(params)
        response = requests.post(server_url + '/v1/orders', json=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        ui.textBrowser_2.append('-----ORDER SUCCESS-----')
        ui.textBrowser_2.append(json.dumps(data, indent=4))
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] Order failed: {e}")
        ui.textBrowser_2.append('-----ORDER FAILED-----')
        ui.textBrowser_2.append(str(e))
    finally:
        ui.textBrowser_2.append('--------------------')


# Function to cancel an order
def close_order(uuid_tmp):
    """
    Cancels a specific order via the Upbit API (authentication required).
    - DELETE /v1/order
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'uuid': uuid_tmp}
    try:
        headers = _get_auth_headers(params)
        response = requests.delete(server_url + '/v1/order', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        print('-----CANCEL SUCCESS-----')
        print(data)
        return data
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"-----CANCEL FAILED-----: {e}")
        return None

# Function to get the history of open orders
def order_wait_history(ticker):
    """
    Fetches the list of open orders (wait, watch) for a specific market from the Upbit API (authentication required).
    - GET /v1/orders/open
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'states[]': ['wait', 'watch']}
    try:
        headers = _get_auth_headers(params)
        response = requests.get(server_url + '/v1/orders/open', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] Failed to fetch open orders: {e}")
        return pd.DataFrame()

# Function to get the history of closed or cancelled orders
def order_close_history(ticker, time):
    """
    Fetches the list of closed (done) or cancelled (cancel) orders for a specific market from the Upbit API (authentication required).
    - GET /v1/orders/closed
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'states[]': ['done', 'cancel'], 'end_time': time}
    try:
        headers = _get_auth_headers(params)
        response = requests.get(server_url + '/v1/orders/closed', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] Failed to fetch closed/cancelled orders: {e}")
        return pd.DataFrame()
