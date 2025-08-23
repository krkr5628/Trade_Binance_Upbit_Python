# -*- coding: utf-8 -*-
"""
[File: Main.py]
[Author: Jules (AI Agent)]
[Date: 2025-08-23]

[Summary]
This module is the main entry point of the automated trading program.
It initializes the PySide6 GUI application, connects the UI with the backend logic,
and acts as the top-level orchestrator for the program's execution flow.

[Global Variables]
- `file_path1` (str): Path to the API key settings file.
- `file_path2` (str): Path to the historical candle data CSV file.
- `file_path3` (str): Path to the technical indicator settings file.
- `ticker` (str): The default cryptocurrency ticker to be displayed.

[Dependencies & Interconnections]

[Incoming Calls (External modules calling this module)]
- None (This is the starting point of the program).

[Outgoing Calls (This module calling external modules)]
- `main()` -> `function.file_load()`: Loads API keys into environment variables at startup.
- `main()` -> `function_feature.feature_inital_match()`: Initializes default parameters for technical indicator calculations.
- `main()` -> `function_complex.setting_initial()`: Sets up the initial UI state (e.g., combo box).
- `main()` -> `function_complex.Account()`, `Order_Complete()`, `Order_Wait()`: Displays initial account and order data in the UI at startup.
- `main()` -> `function_complex.Candle_initial_update()`: Loads initial candle data for the chart at startup.
- `showTime()` (internal timer function) -> `function_complex.Candle_update()`: Called every minute to update candle data and related indicators.
- `showTime()` -> `function_feature.get_prediction()`: Called every minute to get a new dummy prediction.
- `refresh()` (internal button handler) -> `function_complex.Account()`, `Order_Wait()`, `Order_Complete()`: Refreshes relevant UI info when the 'REFRESH' button is clicked.
- `order()` (internal button handler) -> `function_complex.hoga()`: Gets the price for a limit order based on the selected order book level.
- `order()` -> `function.open_order()`: Places the actual buy order based on calculated info when the 'ORDER' button is clicked.
- `main()` -> `function_real.web_socket_initial()`: Starts the real-time ticker WebSocket connection as an asyncio task at startup.

[Global Variable Access]
- `showTime()` -> `function_complex.candle_df_features` (READ): Reads this variable to check for the latest features and pass them to the prediction function.
"""

# Upbit API Notes & Limits
# - Rate Limits: 8 requests/sec for orders, 30/sec for others (REST); 5/sec for WebSocket connections.
# - Order Errors: insufficient_funds_ask/bid, under_min_total_ask/bid (min 5,000 KRW).
# ... (other notes)

# Import necessary modules
import function  # Module for API-related functions
import function_real  # Module for real-time WebSocket functions
import function_feature  # Module for technical indicator calculation functions
import function_complex  # Module for complex business logic and UI integration

import pandas as pd
import numpy as np
from datetime import datetime
import time
import asyncio

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow  # UI Layout
from qasync import QEventLoop  # Event loop for using Qt with asyncio
from PySide6.QtGui import QStandardItemModel, QStandardItem

import tkinter as tk
from tkinter import ttk

# scikit-learn libraries for machine learning models
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# Libraries for API authentication and requests
import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote

# File Paths
file_path1 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_setting.txt" # API settings file
file_path2 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\Goole Drive\\Data\\SOL_Data_Test_1m_Recent_Indicator3_essential.csv" # Historical data file
file_path3 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_feature_setting.txt" # Technical indicator settings file
file_path4 = "" # Path for the trained model file (currently empty)
ticker = "KRW-XRP"  # Default trading ticker
candle_row = 216000 # Number of candle rows (currently unused)

# Main execution function
def main():

    # Create PyQt6 application
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    # Instantiate UI class and set up the UI on the main window
    ui = Ui_MainWindow()
    ui.setupUi(main_window)

    # Load API keys
    function.file_load(file_path1)

    # Load technical indicator settings (currently commented out)
    #function.file_load(file_path3)

    # Initialize technical indicators
    function_feature.feature_inital_match()
    #function_feature.feature_match() # Matching based on user settings (currently commented out)

    # Initialize UI (e.g., combo box)
    function_complex.setting_initial(ui)

    # Display account and asset information
    function_complex.Account(ui, ticker)

    # Display completed/cancelled orders from the last hour
    function_complex.Order_Complete(ui, ticker)

    # Display currently open orders
    function_complex.Order_Wait(ui, ticker)

    # Load and display initial candle data from local CSV and API
    function_complex.Candle_initial_update(ui, ticker, file_path2)

    # Load initial candle data only from API (currently commented out)
    #function_complex.Candle_initial(ui, ticker)

    # Internal function for displaying time and handling periodic updates
    def showTime():

        # Get current time and display it on the UI's LCD widget
        time = QDateTime.currentDateTime()
        ui.lcdNumber.display(time.toString('yyyy-MM-dd HH:mm:ss'))

        # Update candle data every minute (at the 5-second mark)
        if time.time().second() == 5:
            function_complex.Candle_update(time, ticker, ui)

            # Prediction function (using dummy model)
            # Get latest feature data and pass it to the prediction function
            if 'candle_df_features' in function_complex.__dict__ and not function_complex.candle_df_features.empty:
                latest_features = function_complex.candle_df_features.tail(1)
                prediction = function_feature.get_prediction(latest_features)
                # Display prediction result on UI's label_4
                ui.label_4.setText(f"AI Prediction: {prediction}")

    # Set up a timer to call showTime every second
    timer = QTimer()
    timer.timeout.connect(showTime)
    timer.start(1000)

    # Internal function to be called when 'REFRESH' button is clicked
    def refresh():
        # Refresh account, open orders, and completed orders info
        function_complex.Account(ui, ticker)
        function_complex.Order_Wait(ui, ticker)
        function_complex.Order_Complete(ui, ticker)
    # Connect the refresh function to the 'pushButton_8' (REFRESH button)
    ui.pushButton_8.clicked.connect(refresh)

    # Internal function to be called when 'ORDER' button is clicked
    def order():
        """
        Executes a buy order based on information from the UI.
        - Handles limit/market order types.
        - Checks for the minimum order amount (5,000 KRW).
        - Validates input.
        """
        price_volume_input = ui.textEdit_2.toPlainText()

        # Validate input
        if not price_volume_input.strip():
            ui.textBrowser_2.append("[Warning] Order amount or quantity is required.")
            return
        try:
            price_volume_value = float(price_volume_input)
        except ValueError:
            ui.textBrowser_2.append("[Error] Order input must be a number.")
            return

        # Initialize order parameters
        order_price = '0'
        order_volume = '0'
        selected_ord_type = ui.comboBox.currentText()

        # Set parameters and validate based on order type
        if selected_ord_type == 'Market':
            ord_type = 'price'  # Market buy
            order_price = price_volume_input  # For market buys, 'price' is the total order amount
            # Check for minimum order amount
            if price_volume_value < 5000:
                ui.textBrowser_2.append("[Warning] Minimum order amount is 5,000 KRW.")
                return
        else:
            ord_type = 'limit'  # Limit order
            order_volume = price_volume_input  # For limit orders, this is the order quantity
            # Get the price for the limit order
            hoga_price = function_complex.hoga(ticker, selected_ord_type)
            if hoga_price is None:
                ui.textBrowser_2.append(f"[Error] Failed to get orderbook price for {selected_ord_type}. Aborting order.")
                return
            order_price = str(hoga_price)
            # Check for minimum order amount
            if price_volume_value * hoga_price < 5000:
                ui.textBrowser_2.append(f"[Warning] Minimum order amount is 5,000 KRW. (Current: {price_volume_value * hoga_price:,.0f} KRW)")
                return

        # Execute order
        ui.textBrowser_2.append(f"Executing Order: {ticker} / {ord_type} / Price:{order_price} / Volume:{order_volume}")
        function.open_order(ticker, 'bid', ord_type, order_volume, order_price, ui)

        # Refresh info after placing order
        refresh()

    # Connect the order function to 'pushButton_11' (ORDER button)
    ui.pushButton_11.clicked.connect(order)

    # Show the main window
    main_window.show()

    # Set up the event loop for asynchronous WebSocket handling
    loop = QEventLoop(app)
    # Start the WebSocket connection and real-time ticker
    loop.create_task(function_real.web_socket_initial(ui))
    # Run the event loop
    loop.run_forever()


# Call the main function when this script is executed directly
if __name__ == "__main__":
    main()