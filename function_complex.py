# 필요한 모듈 임포트
import datetime
from datetime import datetime
import time
import pandas as pd
import re

# 다른 모듈 임포트
import function
import function_real
import function_feature

# PySide6 UI 관련 모듈 임포트
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow
from qasync import QEventLoop
from PySide6.QtGui import QStandardItemModel, QStandardItem

# pandas DataFrame을 QTableView에 표시하기 위한 커스텀 모델 클래스
class DataFrameModel(QAbstractTableModel):
    """
    pandas DataFrame을 QTableView에 표시하기 위한 Qt 모델.
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

# UI 초기 설정을 위한 함수
def setting_initial(ui):
    """
    애플리케이션 시작 시 UI의 초기 상태를 설정합니다.
    - 주문 유형 콤보박스에 항목 추가 및 기본값 설정
    """
    initial_values = ["Ask5", "Ask4", "Ask3", "Ask2", "Ask1", "Market", "Bid1", "Bid2", "Bid3", "Bid4", "Bid5"]
    ui.comboBox.addItems(initial_values)
    market_index = initial_values.index("Market")
    ui.comboBox.setCurrentIndex(market_index)

# 실시간 수익률 계산을 위한 전역 변수 (평균 매수 단가)
avg_price = 0

# 계좌 정보 및 보유 자산을 UI에 업데이트하는 함수
def Account(ui, ticker):
    """
    API를 통해 계좌 정보를 가져와 가공한 후, UI의 테이블뷰에 표시합니다.
    - 보유 자산 필터링 (1000원 이상)
    - DataFrame을 QStandardItemModel로 변환하여 체크박스 기능 추가
    - '청산' 버튼에 대한 이벤트 핸들러 연결
    """
    hold_df = function.hold_account()
    if not hold_df.empty:
        global avg_price
        ticker_currency = ticker.split('-')[1]
        avg_price_filter = hold_df[hold_df['currency'] == ticker_currency]
        if not avg_price_filter.empty:
            avg_price = avg_price_filter['avg_buy_price'].values[0]

        # 데이터 타입 변환 및 총 평가액 계산
        hold_df['balance'] = hold_df['balance'].astype(float)
        hold_df['avg_buy_price'] = hold_df['avg_buy_price'].astype(float)
        hold_df['Total_KRW'] = hold_df['balance'] * hold_df['avg_buy_price']

        # 1000원 이상 보유 자산 및 원화(KRW)만 필터링
        krw_items = hold_df[(hold_df['Total_KRW'] >= 1000)]
        cash_item = hold_df[hold_df['currency'] == 'KRW']
        result_df = pd.concat([cash_item, krw_items])
        result_df['Select'] = False  # 체크박스 선택 상태 저장을 위한 'Select' 열 추가

        # QStandardItemModel을 사용하여 테이블뷰에 데이터 표시 (체크박스 포함)
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

        # '청산' 버튼 클릭 시 선택된 항목을 시장가 매도하는 함수
        def clear_selected_orders():
            for row in range(hold_model.rowCount()):
                if hold_model.item(row, result_df.columns.get_loc('Select')).checkState() == Qt.Checked:
                    if hold_model.item(row, result_df.columns.get_loc('currency')).text() == 'KRW':
                        continue

                    # 선택된 코인의 티커와 매도 가능 수량 계산
                    ticker_to_clear = hold_model.item(row, result_df.columns.get_loc('unit_currency')).text() + '-' + hold_model.item(row, result_df.columns.get_loc('currency')).text()
                    volume_order = str(float(hold_model.item(row, result_df.columns.get_loc('balance')).text()) - float(hold_model.item(row, result_df.columns.get_loc('locked')).text()))

                    ui.textBrowser_2.append(f"Clear order: {ticker_to_clear} / market / {volume_order}")
                    function.open_order(ticker_to_clear, 'ask', 'market', volume_order, 'null', ui)

            # 정보 새로고침
            Account(ui, ticker)
            Order_Wait(ui, ticker)
            Order_Complete(ui, ticker)

        # 버튼 클릭 시그널을 연결합니다.
        # 이 함수(Account)는 새로고침 시마다 호출되므로, 중복 연결을 방지하기 위해
        # 기존의 연결을 먼저 끊고(disconnect) 다시 연결(connect)합니다.
        try:
            ui.pushButton_6.clicked.disconnect()
        except RuntimeError:
            # 연결이 없는 경우 RuntimeError가 발생할 수 있으므로 pass 처리
            pass
        ui.pushButton_6.clicked.connect(clear_selected_orders)
    else:
        # 보유 자산이 없을 경우 테이블 비우기
        ui.tableView_7.setModel(QStandardItemModel())

# 미체결 주문을 UI에 업데이트하는 함수
def Order_Wait(ui, ticker):
    """
    API를 통해 미체결 주문 내역을 가져와 UI의 테이블뷰에 표시합니다.
    - QStandardItemModel을 사용하여 체크박스 기능 추가
    - '취소' 버튼에 대한 이벤트 핸들러 연결
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

        # '취소' 버튼 클릭 시 선택된 주문을 취소하는 함수
        def cancel_selected_orders():
            for row in range(order_wait_model.rowCount()):
                if order_wait_model.item(row, order_wait_data_filtered.columns.get_loc('Select')).checkState() == Qt.Checked:
                    uuid = order_wait_model.item(row, order_wait_data_filtered.columns.get_loc('uuid')).text()
                    ui.textBrowser_2.append(f"Canceling order: {uuid}")
                    function.close_order(uuid)

            # 정보 새로고침
            Account(ui, ticker)
            Order_Wait(ui, ticker)
            Order_Complete(ui, ticker)

        # 버튼 클릭 시그널을 연결합니다.
        # 이 함수(Order_Wait)는 새로고침 시마다 호출되므로, 중복 연결을 방지하기 위해
        # 기존의 연결을 먼저 끊고(disconnect) 다시 연결(connect)합니다.
        try:
            ui.pushButton_10.clicked.disconnect()
        except RuntimeError:
            # 연결이 없는 경우 RuntimeError가 발생할 수 있으므로 pass 처리
            pass
        ui.pushButton_10.clicked.connect(cancel_selected_orders)
    else:
        # 미체결 주문이 없을 경우 테이블 비우기
        ui.tableView_3.setModel(QStandardItemModel())

# 완료/취소된 주문을 UI에 업데이트하는 함수
def Order_Complete(ui, ticker):
    """
    API를 통해 최근 1시간 내의 완료/취소된 주문 내역을 가져와 UI 테이블뷰에 표시합니다.
    - DataFrameModel을 사용하여 간단하게 표시
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

# 캔들 데이터 저장을 위한 전역 DataFrame
candle_df_filterd_display = pd.DataFrame()  # UI 표시용
candle_df_features = pd.DataFrame()         # 기술적 지표 포함 전체 데이터용

# 초기 캔들 데이터를 로드하고 UI에 표시하는 함수
def Candle_initial_update(ui, ticker, path2):
    """
    프로그램 시작 시 초기 캔들 데이터를 설정합니다.
    현재는 Upbit API를 통해 최근 60개의 1분봉 데이터를 가져와 UI에 표시하는 간단한 로직을 사용합니다.
    (주석 처리된 코드는 로컬 데이터와 API 데이터를 병합하는 더 복잡한 로직의 흔적입니다.)
    """
    global candle_df_filterd_display
    global candle_df_features

    # API를 통해 최근 60개의 1분봉 데이터를 가져옵니다.
    candle_df = function.candle(1, ticker, 60, 0)

    # 데이터가 없을 경우 함수 종료
    if candle_df.empty:
        print("[ERROR] 초기 캔들 데이터를 가져오지 못했습니다.")
        return

    # 첫 번째 행은 현재 진행중인 캔들이므로 제외
    candle_df = candle_df.iloc[1:]

    # 컬럼 이름 변경
    candle_df.rename(columns={'candle_date_time_utc': 'UTC', 'candle_date_time_kst': 'KST', 'trade_price': 'close',
                              'opening_price': 'open', 'high_price': 'high', 'low_price': 'low'}, inplace=True)

    # UI에 티커 이름 설정
    if not candle_df.empty:
        ui.label.setText(candle_df["market"].iloc[0])

    # 표시할 컬럼만 선택하고, 최신순으로 정렬
    candle_df_filterd_display = candle_df[['UTC', 'KST', 'close', 'open', 'high', 'low']].iloc[::-1].reset_index(drop=True)

    # UI 테이블뷰에 모델 설정
    candle_model = DataFrameModel(candle_df_filterd_display)
    ui.tableView_5.setModel(candle_model)
    ui.tableView_5.resizeColumnsToContents()
    ui.tableView_5.verticalHeader().setVisible(False)
    header = ui.tableView_5.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

# 1분마다 캔들 데이터를 업데이트하는 함수
def Candle_update(time_qt, ticker, ui):
    """
    1분마다 새로운 캔들 데이터를 API에서 가져와 기존 데이터에 추가하고 UI를 업데이트합니다.
    """
    global candle_df_filterd_display
    global candle_df_features

    # API 요청을 위한 시간 형식 변환
    time_8061 = time_qt.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"

    # 최신 1분봉 데이터 가져오기
    minute_df = function.candle(1, ticker, 1, time_8061)
    if not minute_df.empty:
        minute_df.rename(columns={'candle_date_time_utc': 'UTC', 'candle_date_time_kst': 'KST', 'trade_price': 'close',
                                  'opening_price': 'open', 'high_price': 'high', 'low_price': 'low'}, inplace=True)
        minute_df_filterd = minute_df[['UTC', 'KST', 'close', 'open', 'high', 'low']]

        # 기존 데이터와 병합하고 최신 데이터가 위로 오도록 정렬
        candle_df_filterd_display = pd.concat([minute_df_filterd, candle_df_filterd_display]).reset_index(drop=True)

        # 기술적 지표 데이터도 업데이트 (현재 주석 처리)
        # candle_df_features = pd.concat([candle_df_features, minute_df_filterd]).reset_index(drop=True)
        # candle_df_features = function_feature.data_feature_1(candle_df_features, 60)

        # UI 테이블뷰 업데이트 (최대 70개 행 유지)
        if len(candle_df_filterd_display) > 70:
            candle_df_filterd_display = candle_df_filterd_display.iloc[:70]

        candle_model = DataFrameModel(candle_df_filterd_display)
        ui.tableView_5.setModel(candle_model)

# 콤보박스에서 선택된 호가 유형에 해당하는 실제 가격을 반환하는 함수
def hoga(ticker, ord_type_hoga):
    """
    'Ask1', 'Bid3' 등과 같은 문자열을 받아 실제 호가로 변환합니다.
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