import pandas as pd

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


def Account(ui) :
    # 계좌 항목
    hold_df = function.hold_account()
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
            else:
                item = QStandardItem(str(value))
            items.append(item)
        hold_model.appendRow(items)

    ui.tableView_7.setModel(hold_model)
    ui.tableView_7.resizeColumnsToContents()
    ui.tableView_7.verticalHeader().setVisible(False)
    header = ui.tableView_7.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

    def clear_selected_orders():
        ui.textBrowser_2.append("TEST1")
        for row in range(hold_model.rowCount()):
            item = hold_model.item(row, result_df.columns.get_loc('Select'))
            if item.checkState() == Qt.Checked:
                uuid = hold_model.item(row, result_df.columns.get_loc('unit_currency')).text() + '-' + hold_model.item(row, result_df.columns.get_loc('currency')).text()
                volume = hold_model.item(row, result_df.columns.get_loc('balance')).text()

                #open_order(ticker, type, ord_type, volume, price)
                function.open_order(uuid, 'ask', 'market', volume, '0')

    ui.pushButton_6.clicked.connect(clear_selected_orders)

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

        # 청산 버튼 이벤트 연결
        def cancel_selected_orders():
            # 'Select'와 'uuid' 열의 인덱스를 미리 가져옵니다.
            select_col = order_wait_data_filtered.columns.get_loc('Select')
            uuid_col = order_wait_data_filtered.columns.get_loc('uuid')

            for row in range(order_wait_model.rowCount()):
                ui.textBrowser_2.append("TEST2")
                item = order_wait_model.item(row, select_col)  # 'Select' 열의 항목을 가져옴
                if item is not None and item.checkState() == Qt.Checked:
                    uuid = order_wait_model.item(row, uuid_col).text()  # 'uuid' 열의 텍스트를 가져옴
                    ui.textBrowser_2.append(f"Canceling order: {uuid}")
                    function.close_order(uuid)

        ui.pushButton_10.clicked.connect(cancel_selected_orders)

def Order_Complete(ui, ticker) :
    # 주문 완료 및 취소 항목(1시간 이내)
    time_close = QDateTime.currentDateTime()
    time_8061_close = time_close.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"
    order_close_data = function.order_close_history(ticker, time_8061_close)
    if not order_close_data.empty:
        order_close_data_filtered = order_close_data[
            ['side', 'ord_type', 'price', 'state', 'created_at', 'volume', 'executed_volume', 'remaining_volume']]
        order_close_model = DataFrameModel(order_close_data_filtered)
        ui.tableView_4.setModel(order_close_model)
        ui.tableView_4.resizeColumnsToContents()
        ui.tableView_4.verticalHeader().setVisible(False)
        header = ui.tableView_4.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

def Candle_initial(ui, ticker) :
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

    return candle_df_filterd