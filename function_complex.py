import pandas as pd
import re

import function
import function_real

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow
from qasync import QEventLoop
from PySide6.QtGui import QStandardItemModel, QStandardItem

class DataFrameModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            elif orientation == Qt.Vertical:
                return self._df.index[section]
        return None

def setting_initial(ui) :
    initial_values = ["Ask5", "Ask4", "Ask3", "Ask2", "Ask1", "Market", "Bid1", "Bid2", "Bid3", "Bid4", "Bid5"]
    ui.comboBox.addItems(initial_values)

    # "Market" 항목을 기본 선택으로 설정
    market_index = initial_values.index("Market")  # "Market"의 인덱스 찾기
    ui.comboBox.setCurrentIndex(market_index)

avg_price = 0

def Account(ui, ticker) :
    # 계좌 항목
    hold_df = function.hold_account()
    if not hold_df.empty :
        # 퍼센트 파악 전용 글로벌 시세
        global avg_price
        ticker_currency = ticker.split('-')[1]
        avg_price_filter = hold_df[hold_df['currency'] == ticker_currency]
        if not avg_price_filter.empty :
            avg_price = avg_price_filter['avg_buy_price'].values[0]

        #
        hold_df['balance'] = hold_df['balance'].astype(float)
        hold_df['avg_buy_price'] = hold_df['avg_buy_price'].astype(float)
        hold_df['Total_KRW'] = hold_df['balance'] * hold_df['avg_buy_price']

        krw_items = hold_df[(hold_df['Total_KRW'] >= 1000)]
        cash_item = hold_df[hold_df['currency'] == 'KRW']
        result_df = pd.concat([cash_item, krw_items])

        # 체크박스 열 추가
        result_df['Select'] = False

        # hold_model = DataFrameModel(result_df)

        hold_model = QStandardItemModel()
        hold_model.setColumnCount(len(result_df.columns))
        hold_model.setHorizontalHeaderLabels(result_df.columns)

        for row in range(len(result_df)):
            items = []
            for col in range(len(result_df.columns)):
                value = result_df.iloc[row, col]
                if col == result_df.columns.get_loc('Select'):  # Select 열에 체크박스 추가
                    item = QStandardItem()
                    item.setCheckable(True)
                    item.setCheckState(Qt.Checked if value else Qt.Unchecked)
                    item.setData(row, Qt.UserRole)  # row 정보를 저장

                    # itemChanged 이벤트를 통해 체크박스 상태 변경 시 데이터 모델에 반영
                    item.setData(False, Qt.UserRole + 1)
                else:
                    item = QStandardItem(str(value))
                items.append(item)
            hold_model.appendRow(items)

        ui.tableView_7.setModel(hold_model)
        ui.tableView_7.resizeColumnsToContents()
        ui.tableView_7.verticalHeader().setVisible(False)
        header = ui.tableView_7.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        def on_item_changed(item):
            if item.isCheckable():
                row = item.data(Qt.UserRole)
                col = result_df.columns.get_loc('Select')
                result_df.iloc[row, col] = (item.checkState() == Qt.Checked)

        # itemChanged 시그널 연결
        hold_model.itemChanged.connect(on_item_changed)

        # 청산 버튼 이벤트 연결
        def clear_selected_orders():
            # 열의 인덱스를 미리 가져옵니다.
            select_col = result_df.columns.get_loc('Select')
            unit_currency_col = result_df.columns.get_loc('unit_currency')
            currency_col = result_df.columns.get_loc('currency')
            volume_col = result_df.columns.get_loc('balance')
            volume_locked_col = result_df.columns.get_loc('locked')

            for row in range(hold_model.rowCount()):
                # 'currency' 열의 항목을 가져옴
                if hold_model.item(row, currency_col).text() == 'KRW':
                    continue

                ticker = hold_model.item(row, unit_currency_col).text() + '-' + hold_model.item(row, currency_col).text()
                volume_order = str(float(hold_model.item(row, volume_col).text()) - float(hold_model.item(row, volume_locked_col).text()))

                # 작업 내용을 UI에 출력
                ui.textBrowser_2.append(f"Clear order: {ticker} / market / {volume_order}")
                # 지정된 매개변수로 function.open_order 호출
                function.open_order(ticker, 'ask', 'market', volume_order, 'null', ui)
                #항목 Refresh
                Account(ui, ticker)
                Order_Wait(ui, ticker)
                Order_Complete(ui, ticker)

        ui.pushButton_6.clicked.connect(clear_selected_orders)

    else :
        empty_model = QStandardItemModel()  # 또는 hold_model = QStandardItemModel()
        ui.tableView_7.setModel(empty_model)  # 빈 모델로 설정하여 기존 내용을 제거

def Order_Wait(ui, ticker) :
    # 주문 대기 및 예약 항목
    order_wait_data = function.order_wait_history(ticker)
    if not order_wait_data.empty:
        order_wait_data_filtered = order_wait_data[
            ['uuid', 'side', 'ord_type', 'price', 'state', 'created_at', 'volume', 'executed_volume',
             'remaining_volume']].copy()

        # order_wait_model = DataFrameModel(order_wait_data_filtered)

        # 체크박스 열 추가
        order_wait_data_filtered.loc[:, 'Select'] = False

        order_wait_model = QStandardItemModel()
        order_wait_model.setColumnCount(len(order_wait_data_filtered.columns))
        order_wait_model.setHorizontalHeaderLabels(order_wait_data_filtered.columns)

        for row in range(len(order_wait_data_filtered)):
            items = []
            for col in range(len(order_wait_data_filtered.columns)):
                value = order_wait_data_filtered.iloc[row, col]
                if col == order_wait_data_filtered.columns.get_loc('Select'):  # Select 열에 체크박스 추가
                    item = QStandardItem()
                    item.setCheckable(True)
                    item.setCheckState(Qt.Checked if value else Qt.Unchecked)
                    item.setData(row, Qt.UserRole)  # row 정보를 저장

                    # itemChanged 이벤트를 통해 체크박스 상태 변경 시 데이터 모델에 반영
                    item.setData(False, Qt.UserRole + 1)
                else:
                    item = QStandardItem(str(value))
                items.append(item)
            order_wait_model.appendRow(items)

        ui.tableView_3.setModel(order_wait_model)
        ui.tableView_3.resizeColumnsToContents()
        ui.tableView_3.verticalHeader().setVisible(False)
        header = ui.tableView_3.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        def on_item_changed(item):
            if item.isCheckable():
                row = item.data(Qt.UserRole)
                col = order_wait_data_filtered.columns.get_loc('Select')
                order_wait_data_filtered.iloc[row, col] = (item.checkState() == Qt.Checked)

        # itemChanged 시그널 연결
        order_wait_model.itemChanged.connect(on_item_changed)

        # 취소 버튼 이벤트 연결
        def cancel_selected_orders():
            # 'Select'와 'uuid' 열의 인덱스를 미리 가져옵니다.
            select_col = order_wait_data_filtered.columns.get_loc('Select')
            uuid_col = order_wait_data_filtered.columns.get_loc('uuid')

            for row in range(order_wait_model.rowCount()):
                item = order_wait_model.item(row, select_col)  # 'Select' 열의 항목을 가져옴
                if item is not None and item.checkState() == Qt.Checked:
                    uuid = order_wait_model.item(row, uuid_col).text()  # 'uuid' 열의 텍스트를 가져옴
                    ui.textBrowser_2.append(f"Canceling order: {uuid}")
                    function.close_order(uuid)
                    # 항목 Refresh
                    Account(ui, ticker)
                    Order_Wait(ui, ticker)
                    Order_Complete(ui, ticker)

        ui.pushButton_10.clicked.connect(cancel_selected_orders)
    else :
        empty_model = QStandardItemModel()  # 또는 hold_model = QStandardItemModel()
        ui.tableView_3.setModel(empty_model)  # 빈 모델로 설정하여 기존 내용을 제거

def Order_Complete(ui, ticker) :
    # 주문 완료 및 취소 항목(1시간 이내)
    time_close = QDateTime.currentDateTime()
    time_8061_close = time_close.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"
    order_close_data = function.order_close_history(ticker, time_8061_close)
    if not order_close_data.empty:
        order_close_data_filtered = order_close_data[
            ['market', 'side', 'ord_type', 'state', 'created_at', 'volume', 'executed_volume', 'remaining_volume']]
        order_close_model = DataFrameModel(order_close_data_filtered)
        ui.tableView_4.setModel(order_close_model)
        ui.tableView_4.resizeColumnsToContents()
        ui.tableView_4.verticalHeader().setVisible(False)
        header = ui.tableView_4.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

candle_df_filterd = pd.DataFrame()

def Candle_initial(ui, ticker) :

    global candle_df_filterd

    # 초기 분봉 업데이트
    candle_df = function.candle(1, ticker, 60, 0).iloc[1:]
    candle_df['candle_date_time_utc'] = pd.to_datetime(candle_df['candle_date_time_utc'])
    candle_df['candle_date_time_kst'] = pd.to_datetime(candle_df['candle_date_time_kst'])
    candle_df.rename(columns={'candle_date_time_utc': 'UTC', 'candle_date_time_kst': 'KST', 'trade_price': 'CLOSE',
                              'opening_price': 'OPEN', 'high_price': 'HIGH', 'low_price': 'LOW'}, inplace=True)
    ui.label.setText(candle_df["market"][1])
    candle_df_filterd = candle_df[['UTC', 'KST', 'CLOSE', 'OPEN', 'HIGH', 'LOW']]

    candle_model = DataFrameModel(candle_df_filterd)
    ui.tableView_5.setModel(candle_model)
    ui.tableView_5.resizeColumnsToContents()
    ui.tableView_5.verticalHeader().setVisible(False)
    header = ui.tableView_5.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

def candle_update(time, ticker, ui):

    global candle_df_filterd

    time_8061 = time.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"

    # 1분 봉 최신 업데이트
    minute_df = function.candle(1, ticker, 1, time_8061)

    minute_df['candle_date_time_utc'] = pd.to_datetime(minute_df['candle_date_time_utc'])
    minute_df['candle_date_time_kst'] = pd.to_datetime(minute_df['candle_date_time_kst'])
    minute_df.rename(columns={'candle_date_time_utc': 'UTC', 'candle_date_time_kst': 'KST', 'trade_price': 'CLOSE',
                                'opening_price': 'OPEN', 'high_price': 'HIGH', 'low_price': 'LOW'}, inplace=True)
    minute_df_filterd = minute_df[['UTC', 'KST', 'CLOSE', 'OPEN', 'HIGH', 'LOW']]
    candle_df_filterd = pd.concat([minute_df_filterd, candle_df_filterd]).reset_index(drop=True)

    if len(candle_df_filterd) > 70:
        candle_df_filterd = candle_df_filterd.iloc[:-1]

        candle_model = DataFrameModel(candle_df_filterd)
        ui.tableView_5.setModel(candle_model)
        ui.tableView_5.resizeColumnsToContents()
        ui.tableView_5.verticalHeader().setVisible(False)
        header = ui.tableView_5.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

def hoga(ticker, ord_type_hoga) :
    hoga_list = function.hoga_list(ticker);
    split_index = len(ord_type_hoga.rstrip('0123456789'))
    hoga_type = ord_type_hoga[:split_index]
    hoga_num = ord_type_hoga[split_index:]
    try:
        if hoga_type == 'Bid':
            return hoga_list['bid_price'].iloc[int(hoga_num) - 1]
        else:
            return hoga_list['ask_price'].iloc[int(hoga_num) - 1]
    except IndexError:
        print(f"IndexError: {hoga_num} is out of range")
        return None
    except KeyError:
        print(f"KeyError: Column not found in hoga_list")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

#def candle_feature() :
