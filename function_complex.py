# -*- coding: utf-8 -*-
"""
[File: function_complex.py]
[Author: Jules (AI Agent)]
[Date: 2025-08-23]

[Summary]
This module serves as the middle layer for the application's core business logic.
It acts as a bridge between the low-level API module (`function.py`) and the UI (`Main.py`),
handling data processing and complex functions for UI updates.

[Global Variables]
- `avg_price` (float): Stores the average buy price of the current ticker.
- `candle_df_filterd_display` (pd.DataFrame): Stores the data to be displayed in the UI's candle chart table.
- `candle_df_features` (pd.DataFrame): Stores the complete candle data that forms the basis for technical indicator calculations.

[Dependencies & Interconnections]

[Incoming Calls (External modules calling this module)]
- `Main.py` -> `setting_initial()`: For initial UI setup.
- `Main.py` -> `Account()`, `Order_Complete()`, `Order_Wait()`: For initializing and refreshing UI data.
- `Main.py` -> `Candle_initial_update()`: For loading initial candle data.
- `Main.py` -> `Candle_update()`: For updating candle data every minute.
- `Main.py` -> `hoga()`: For getting the price for a limit order.

[Outgoing Calls (This module calling external modules)]
- `Account()` -> `function.hold_account()`: To fetch account information.
- `Order_Wait()` -> `function.order_wait_history()`: To fetch open orders.
- `Order_Complete()` -> `function.order_close_history()`: To fetch closed/cancelled orders.
- `Candle_initial_update()` -> `function.candle()`: To fetch initial candle data.
- `Candle_initial_update()` -> `function_feature.data_feature_1()`: For initial indicator calculation.
- `Candle_update()` -> `function.candle()`: To fetch the latest 1-minute candle data.
- `Candle_update()` -> `function_feature.data_feature_1()`: For recalculating indicators every minute.
- `hoga()` -> `function.hoga_list()`: To fetch order book data.
- `clear_selected_orders()` (internal function) -> `function.open_order()`: To place market sell (liquidation) orders.
- `cancel_selected_orders()` (internal function) -> `function.close_order()`: To cancel an order.

[Global Variable Access]
- `Account()`: Updates the global `avg_price` variable.
- `Candle_initial_update()`: Initializes the global `candle_df_filterd_display` and `candle_df_features` variables.
- `Candle_update()`: Updates the global `candle_df_filterd_display` and `candle_df_features` variables.
- `function_real.py` reads the `avg_price` variable from this module.
- `Main.py` reads the `candle_df_features` variable from this module.
"""

# Import necessary modules
import datetime
from datetime import datetime
import time
import pandas as pd
import re

# Import other project modules
import function
import function_real
import function_feature

# Import PySide6 UI modules
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow
from qasync import QEventLoop
from PySide6.QtGui import QStandardItemModel, QStandardItem

# Custom model class to display pandas DataFrames in a QTableView
class DataFrameModel(QAbstractTableModel):
    """
    A Qt model for displaying pandas DataFrames in a QTableView.
    """
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            elif orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None

# Function for initial UI setup
def setting_initial(ui):
    """
    Sets the initial state of the UI when the application starts.
    - Adds items to the order type combo box and sets a default value.
    """
    initial_values = ["Ask5", "Ask4", "Ask3", "Ask2", "Ask1", "Market", "Bid1", "Bid2", "Bid3", "Bid4", "Bid5"]
    ui.comboBox.addItems(initial_values)
    market_index = initial_values.index("Market")
    ui.comboBox.setCurrentIndex(market_index)

# Global variable for average buy price (used for real-time P/L calculation)
avg_price = 0

# Function to update account information and holdings on the UI
def Account(ui, ticker):
    """
    Fetches account information via the API, processes it, and displays it in the UI's table view.
    - Filters assets with a total value >= 1000 KRW.
    - Converts the DataFrame to a QStandardItemModel to add checkbox functionality.
    - Connects an event handler to the 'Liquidate' button.
    """
    hold_df = function.hold_account()
    if not hold_df.empty:
        global avg_price
        ticker_currency = ticker.split('-')[1]
        avg_price_filter = hold_df[hold_df['currency'] == ticker_currency]
        if not avg_price_filter.empty:
            avg_price = avg_price_filter['avg_buy_price'].values[0]

        # Convert data types and calculate total value
        hold_df['balance'] = hold_df['balance'].astype(float)
        hold_df['avg_buy_price'] = hold_df['avg_buy_price'].astype(float)
        hold_df['Total_KRW'] = hold_df['balance'] * hold_df['avg_buy_price']

        # Filter assets worth over 1000 KRW and KRW balance
        krw_items = hold_df[(hold_df['Total_KRW'] >= 1000)]
        cash_item = hold_df[hold_df['currency'] == 'KRW']
        result_df = pd.concat([cash_item, krw_items])
        result_df['Select'] = False  # Add 'Select' column to store checkbox state

        # Use QStandardItemModel to display data in the table view (including checkboxes)
        hold_model = QStandardItemModel()
        hold_model.setColumnCount(len(result_df.columns))
        hold_model.setHorizontalHeaderLabels(result_df.columns)

        for row in range(len(result_df)):
            items = []
            for col_idx, col_name in enumerate(result_df.columns):
                value = result_df.iloc[row, col_idx]
                item = QStandardItem()
                if col_name == 'Select':
                    item.setCheckable(True)
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setText(str(value))
                items.append(item)
            hold_model.appendRow(items)

        ui.tableView_7.setModel(hold_model)
        ui.tableView_7.resizeColumnsToContents()
        ui.tableView_7.verticalHeader().setVisible(False)
        header = ui.tableView_7.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Function to market sell selected items when the 'Liquidate' button is clicked
        def clear_selected_orders():
            for row in range(hold_model.rowCount()):
                if hold_model.item(row, result_df.columns.get_loc('Select')).checkState() == Qt.Checked:
                    if hold_model.item(row, result_df.columns.get_loc('currency')).text() == 'KRW':
                        continue

                    # Calculate the ticker and available volume for the selected coin
                    ticker_to_clear = hold_model.item(row, result_df.columns.get_loc('unit_currency')).text() + '-' + hold_model.item(row, result_df.columns.get_loc('currency')).text()
                    volume_order = str(float(hold_model.item(row, result_df.columns.get_loc('balance')).text()) - float(hold_model.item(row, result_df.columns.get_loc('locked')).text()))

                    ui.textBrowser_2.append(f"Clear order: {ticker_to_clear} / market / {volume_order}")
                    function.open_order(ticker_to_clear, 'ask', 'market', volume_order, 'null', ui)

            # Refresh information
            Account(ui, ticker)
            Order_Wait(ui, ticker)
            Order_Complete(ui, ticker)

        # Connect the button's clicked signal.
        # Since this function (Account) is called on every refresh, we first disconnect
        # any existing connection to prevent duplicate signal handlers.
        try:
            ui.pushButton_6.clicked.disconnect()
        except RuntimeError:
            # A RuntimeError can occur if there's no connection, so we pass.
            pass
        ui.pushButton_6.clicked.connect(clear_selected_orders)
    else:
        # Clear the table if there are no assets
        ui.tableView_7.setModel(QStandardItemModel())

# Function to update open orders on the UI
def Order_Wait(ui, ticker):
    """
    Fetches open orders via the API and displays them in the UI's table view.
    - Adds checkbox functionality using QStandardItemModel.
    - Connects an event handler to the 'Cancel' button.
    """
    order_wait_data = function.order_wait_history(ticker)
    if not order_wait_data.empty:
        order_wait_data_filtered = order_wait_data[
            ['uuid', 'side', 'ord_type', 'price', 'state', 'created_at', 'volume', 'executed_volume', 'remaining_volume']
        ].copy()
        order_wait_data_filtered['Select'] = False

        order_wait_model = QStandardItemModel()
        order_wait_model.setHorizontalHeaderLabels(order_wait_data_filtered.columns)

        for row in range(len(order_wait_data_filtered)):
            items = []
            for col_idx, col_name in enumerate(order_wait_data_filtered.columns):
                value = order_wait_data_filtered.iloc[row, col_idx]
                item = QStandardItem()
                if col_name == 'Select':
                    item.setCheckable(True)
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setText(str(value))
                items.append(item)
            order_wait_model.appendRow(items)

        ui.tableView_3.setModel(order_wait_model)
        ui.tableView_3.resizeColumnsToContents()
        ui.tableView_3.verticalHeader().setVisible(False)
        header = ui.tableView_3.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Function to cancel selected orders when the 'Cancel' button is clicked
        def cancel_selected_orders():
            for row in range(order_wait_model.rowCount()):
                if order_wait_model.item(row, order_wait_data_filtered.columns.get_loc('Select')).checkState() == Qt.Checked:
                    uuid = order_wait_model.item(row, order_wait_data_filtered.columns.get_loc('uuid')).text()
                    ui.textBrowser_2.append(f"Canceling order: {uuid}")
                    function.close_order(uuid)

            # Refresh information
            Account(ui, ticker)
            Order_Wait(ui, ticker)
            Order_Complete(ui, ticker)

        # Connect the button's clicked signal, disconnecting first to prevent duplicates.
        try:
            ui.pushButton_10.clicked.disconnect()
        except RuntimeError:
            # A RuntimeError can occur if there's no connection, so we pass.
            pass
        ui.pushButton_10.clicked.connect(cancel_selected_orders)
    else:
        # Clear the table if there are no open orders
        ui.tableView_3.setModel(QStandardItemModel())

# Function to update completed/cancelled orders on the UI
def Order_Complete(ui, ticker):
    """
    Fetches completed/cancelled orders from the last hour via the API and displays them in the UI.
    - Uses DataFrameModel for simple display.
    """
    time_close = QDateTime.currentDateTime()
    utc_time = time_close.toUTC()
    time_8061_close = utc_time.toString("yyyy-MM-dd'T'HH:mm:ss'Z'")
    order_close_data = function.order_close_history(ticker, time_8061_close)
    if not order_close_data.empty:
        order_close_data_filtered = order_close_data[
            ['market', 'side', 'ord_type', 'state', 'created_at', 'volume', 'executed_volume', 'remaining_volume']
        ]
        order_close_model = DataFrameModel(order_close_data_filtered)
        ui.tableView_4.setModel(order_close_model)
        ui.tableView_4.resizeColumnsToContents()
        ui.tableView_4.verticalHeader().setVisible(False)
        header = ui.tableView_4.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

# Global DataFrames for candle data
candle_df_filterd_display = pd.DataFrame()  # For UI display
candle_df_features = pd.DataFrame()         # For technical indicators

# Function to load and display initial candle data
def Candle_initial_update(ui, ticker, path2):
    """
    Sets the initial candle data when the application starts.
    Currently uses a simple logic to fetch the last 60 1-minute candles from the Upbit API.
    (Commented out code contains remnants of a more complex logic for merging local and API data).
    """
    global candle_df_filterd_display
    global candle_df_features

    # Fetch the last 60 1-minute candles via the API
    candle_df = function.candle(1, ticker, 60, 0)

    # Exit if data could not be fetched
    if candle_df.empty:
        print("[ERROR] Could not fetch initial candle data.")
        return

    # Exclude the first row as it's the currently forming candle
    candle_df = candle_df.iloc[1:]

    # Rename columns
    candle_df.rename(columns={'candle_date_time_utc': 'UTC', 'candle_date_time_kst': 'KST', 'trade_price': 'close',
                              'opening_price': 'open', 'high_price': 'high', 'low_price': 'low'}, inplace=True)

    # Set the ticker name on the UI
    if not candle_df.empty:
        ui.label.setText(candle_df["market"].iloc[0])

    # Select only the columns to be displayed and sort by most recent
    candle_df_filterd_display = candle_df[['UTC', 'KST', 'close', 'open', 'high', 'low']].iloc[::-1].reset_index(drop=True)

    # Calculate technical indicators (using the full dataset, not just the display version)
    # Note: Long-term indicators may be inaccurate as only 60 candles are used.
    if not candle_df.empty:
        candle_df_features = function_feature.data_feature_1(candle_df.iloc[::-1]) # Pass in original chronological order
        print("Initial technical indicators calculated.")

    # Set the model for the UI table view
    candle_model = DataFrameModel(candle_df_filterd_display)
    ui.tableView_5.setModel(candle_model)
    ui.tableView_5.resizeColumnsToContents()
    ui.tableView_5.verticalHeader().setVisible(False)
    header = ui.tableView_5.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

# Function to update candle data every minute
def Candle_update(time_qt, ticker, ui):
    """
    Fetches the new 1-minute candle from the API every minute, adds it to the existing data, and updates the UI.
    """
    global candle_df_filterd_display
    global candle_df_features

    # Convert time format for the API request
    time_8061 = time_qt.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"

    # Fetch the latest 1-minute candle
    minute_df = function.candle(1, ticker, 1, time_8061)
    if not minute_df.empty:
        minute_df.rename(columns={'candle_date_time_utc': 'UTC', 'candle_date_time_kst': 'KST', 'trade_price': 'close',
                                  'opening_price': 'open', 'high_price': 'high', 'low_price': 'low'}, inplace=True)
        minute_df_filterd = minute_df[['UTC', 'KST', 'close', 'open', 'high', 'low']]

        # Prepend the new candle to the existing data and sort by most recent
        candle_df_filterd_display = pd.concat([minute_df_filterd, candle_df_filterd_display]).reset_index(drop=True)

        # Update technical indicator data
        # Add the new candle to the full dataset and recalculate indicators on the last N candles to prevent performance degradation
        if 'candle_df_features' in globals() and not candle_df_features.empty:
             # Assuming candle_df_features is in ascending chronological order
            temp_df_features = pd.concat([candle_df_features, minute_df]).reset_index(drop=True)
            # Recalculate on the last 200 candles (or max period needed for indicators) to avoid slowdown
            candle_df_features = function_feature.data_feature_1(temp_df_features.tail(200))

        # Update the UI table view (maintaining a max of 70 rows)
        if len(candle_df_filterd_display) > 70:
            candle_df_filterd_display = candle_df_filterd_display.iloc[:70]

        candle_model = DataFrameModel(candle_df_filterd_display)
        ui.tableView_5.setModel(candle_model)

# Function to get the actual price for a selected order book level from the combo box
def hoga(ticker, ord_type_hoga):
    """
    Converts a string like 'Ask1' or 'Bid3' into an actual price from the order book.
    """
    hoga_list_df = function.hoga_list(ticker)
    if hoga_list_df.empty:
        return None

    split_index = len(ord_type_hoga.rstrip('0123456789'))
    hoga_type = ord_type_hoga[:split_index]
    hoga_num = int(ord_type_hoga[split_index:]) - 1

    try:
        if hoga_type == 'Bid':
            return hoga_list_df['bid_price'].iloc[hoga_num]
        else:
            return hoga_list_df['ask_price'].iloc[hoga_num]
    except (IndexError, KeyError) as e:
        print(f"Error getting hoga price: {e}")
        return None