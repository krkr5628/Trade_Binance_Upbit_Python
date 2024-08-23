#Content Type : application/json; charset=utf-8
#query_hash와 query_hash_alg 필드 => 인코딩 되지 않는 쿼리 문자열=> JSON, JWT, 기타 포맷 금지
#Signature 생성시 secret 인코딩 옵션을 확인 => secret key는 base64로 encoding되어 있지 않는다.
#주문 API 초당 8회
#주문 API 외 초당 30회
#WebSocket 데이터 연결 초당 5회
#WebSocket 데이터 요청 초당 5회 분당 100회 => Priavte 정보 계정 당, Public 정보 IP 당
#REST API 데이터 요청 초당 10회
#호출 시 남아있는 요청 수는 REMAINING-Req 응답 헤더 => default 그룹에서 확인 가능
#create_ask_error, create_bid_error : 주문 정보 틀림(시장가 주문 가격 입력 금지)
#insufficient_funds_ask, insufficient_funds_bid : 잔고 부족
#under_min_total_ask, under_min_total_bid : 최소 주문 가격 미만(5,000)
#validation_error : 누락된 파라미터 존재
#expired_access_key : API 키 만료
#no_authorization_i_p : 비허용 IP
#out_of_scope : 기능 신청 안함
#호가표 존재 빢쏌

import function
import function_real

import pandas as pd
import numpy as np
from datetime import datetime
import time
import asyncio

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow
from qasync import QEventLoop
from PyQt6.QtGui import QTextCursor, QTextBlockFormat

import tkinter as tk
from tkinter import ttk

from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote

ticker = "KRW-XRP"

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

def main():
    function.file_load() #API KEYS LOAD

    #초기 윈도우 생성
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    # Ui_MainWindow 인스턴스 생성
    ui = Ui_MainWindow()
    ui.setupUi(main_window)  # QMainWindow에 UI 설정

    # 시간 표시 및 시간 관련 이벤트 처리
    def showTime():

        nonlocal candle_df_filterd

        # 현재 시각 가져오기
        time = QDateTime.currentDateTime()
        ui.lcdNumber.display(time.toString('yyyy-MM-dd HH:mm:ss'))

        # 00초
        if time.time().second() == 5:
            candle_update(time)

    timer = QTimer()
    timer.timeout.connect(showTime)
    timer.start(1000)  # 60초마다 업데이트

    #계좌 항목
    hold_df = function.hold_account()
    hold_df['balance'] = hold_df['balance'].astype(float)
    hold_df['avg_buy_price'] = hold_df['avg_buy_price'].astype(float)
    hold_df['Total_KRW'] = hold_df['balance']*hold_df['avg_buy_price']

    krw_items = hold_df[(hold_df['Total_KRW'] >= 1000)]
    cash_item = hold_df[hold_df['currency'] == 'KRW']
    result_df = pd.concat([cash_item, krw_items])

    hold_model = DataFrameModel(result_df)
    ui.tableView_7.setModel(hold_model)
    ui.tableView_7.resizeColumnsToContents()
    ui.tableView_7.verticalHeader().setVisible(False)
    header = ui.tableView_7.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

    #주문 대기 및 예약 항목
    order_wait_data = function.order_wait_history(ticker)
    if not order_wait_data.empty :
        order_wait_data_filtered = order_wait_data[['side', 'ord_type', 'price', 'state', 'created_at', 'volume', 'executed_volume', 'remaining_volume']]
        order_wait_model = DataFrameModel(order_wait_data_filtered)
        ui.tableView_3.setModel(order_wait_model)
        ui.tableView_3.resizeColumnsToContents()
        ui.tableView_3.verticalHeader().setVisible(False)
        header = ui.tableView_3.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    #주문 완료 및 취소 항목(1시간 이내)
    time_close = QDateTime.currentDateTime()
    time_8061_close = time_close.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"
    order_close_data = function.order_close_history(ticker, time_8061_close)
    if not order_close_data.empty:
        order_close_data_filtered = order_close_data[['side', 'ord_type', 'price', 'state', 'created_at', 'volume', 'executed_volume', 'remaining_volume']]
        order_close_model = DataFrameModel(order_close_data_filtered)
        ui.tableView_4.setModel(order_close_model)
        ui.tableView_4.resizeColumnsToContents()
        ui.tableView_4.verticalHeader().setVisible(False)
        header = ui.tableView_4.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    #초기 분봉 업데이트
    candle_df = function.candle(1, ticker, 60, 0).iloc[1:]
    candle_df['candle_date_time_utc'] = pd.to_datetime(candle_df['candle_date_time_utc'])
    candle_df['candle_date_time_kst'] = pd.to_datetime(candle_df['candle_date_time_kst'])
    candle_df.rename(columns={'candle_date_time_utc': 'UTC','candle_date_time_kst': 'KST', 'trade_price' : 'CLOSE', 'opening_price' : 'OPEN', 'high_price' : 'HIGH', 'low_price' : 'LOW'}, inplace=True)
    ui.label.setText(candle_df["market"][1])
    candle_df_filterd = candle_df[['UTC', 'KST', 'CLOSE', 'OPEN', 'HIGH', 'LOW']]

    candle_model = DataFrameModel(candle_df_filterd)
    ui.tableView_5.setModel(candle_model)
    ui.tableView_5.resizeColumnsToContents()
    ui.tableView_5.verticalHeader().setVisible(False)
    header = ui.tableView_5.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

    # 분봉 업데이트(1분 주기)
    def candle_update(time):

        nonlocal candle_df_filterd

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

    #버튼 처리
    def on_pushButton_10_clicked():
        ui.textBrowser_2.append("TEST COMPLETE")

    ui.pushButton_10.clicked.connect(on_pushButton_10_clicked)

    # 메인 윈도우 보여주기 및 애플리케이션 실행
    main_window.show()

    # WebSocket 비동기 처리
    loop = QEventLoop(app)
    loop.create_task(function_real.web_socket_initial(ui))
    loop.run_forever()

    #
    #function_real.web_scoket_initial()

if __name__ == "__main__":
    main()