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

import pandas as pd
import numpy as np
from datetime import datetime
import time

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow



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


def create_scrollable_frame(container, bg_color):
    # 캔버스 생성
    canvas = tk.Canvas(container, bg=bg_color)
    canvas.grid(row=0, column=0, sticky="nsew")

    # 스크롤바 생성
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # 스크롤 가능한 프레임 생성
    scrollable_frame = tk.Frame(canvas, bg=bg_color)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    return scrollable_frame

def window_main() :
    # 루트 창 생성
    root = tk.Tk()
    root.title("Binance_Upbit_TCN_TRANSFORMER")
    root.geometry("1280x720")

    # 각 row와 column이 동일한 비율로 확장되도록 설정
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)

    #정보 호출
    rst_df1 = function.hold_account() #ACOUNT CASH INFO
    rst_df2 = function.trasaction_history("KRW-SOL") #TRANSACTION INFO

    # 프레임 1
    frame1 = tk.Frame(root, bg="lightblue")
    frame1.grid(row=0, column=0, sticky="nsew")
    label1 = tk.Label(frame1, text="Frame 1", bg="lightblue")
    label1.pack()
    tree1 = ttk.Treeview(frame1, columns=list(rst_df1.columns), show="headings")
    for col in rst_df1.columns:
        tree1.heading(col, text=col)
        tree1.column(col, width=100)
    for _, row in rst_df1.iterrows():
        tree1.insert("", "end", values=list(row))
    tree1.pack(expand=True, fill='both')

    # 프레임 2
    frame2 = tk.Frame(root, bg="lightgreen")
    frame2.grid(row=0, column=1, sticky="nsew")
    label2 = tk.Label(frame2, text="Frame 2", bg="lightgreen")
    label2.pack()
    tree2 = ttk.Treeview(frame2, columns=list(rst_df2.columns), show="headings")
    for col in rst_df2.columns:
        tree2.heading(col, text=col)
        tree2.column(col, width=100)
    for _, row in rst_df2.iterrows():
        tree2.insert("", "end", values=list(row))
    tree2.pack(expand=True, fill='both')

    # 루프 시작
    root.mainloop()

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

    #
    app = QApplication(sys.argv)

    # QMainWindow 인스턴스 생성
    main_window = QMainWindow()

    # Ui_MainWindow 인스턴스 생성
    ui = Ui_MainWindow()
    ui.setupUi(main_window)  # QMainWindow에 UI 설정

    #계좌 항목 출력
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
    header = ui.tableView_7.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.Stretch)

    #초기 분봉 업데이트
    candle_df = function.candle(1, "KRW-SOL", 60, 0).iloc[1:]
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

    def candle_update(time):

        nonlocal candle_df_filterd

        time_8061 = time.toString("yyyy-MM-dd'T'HH:mm") + ":00+09:00"
        # 1분 봉 최신 업데이트
        minute_df = function.candle(1, "KRW-SOL", 1, time_8061)
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

    #시간 표시 및 시간 관련 이벤트 처리
    def showTime():

        nonlocal candle_df_filterd

        # 현재 시각 가져오기
        time = QDateTime.currentDateTime()
        ui.lcdNumber.display(time.toString('yyyy-MM-dd HH:mm:ss'))

        #00초
        if time.time().second() == 5 :
            candle_update(time)


    timer = QTimer()
    timer.timeout.connect(showTime)
    timer.start(1000)  # 60초마다 업데이트


    #timer2 = QTimer()
    #timer2.timeout.connect(candle_update)
    #timer2.start(60 * 1000)  # 60초마다 업데이트

    #버튼 처리
    def on_pushButton_10_clicked():
        ui.textBrowser_2.append("TEST COMPLETE")

    ui.pushButton_10.clicked.connect(on_pushButton_10_clicked)


    # 메인 윈도우 보여주기
    main_window.show()

    # 애플리케이션 실행
    sys.exit(app.exec())

    # function.Market_Data_Specific("KRW-SOL")  # SPECFIC TIKCER INFO
    #function.candle(1,"KRW-BTC",5) #CANDLE
    #function.order_possible("KRW-SOL")
    #function.open_order("KRW-SOL")
    #function.closed_order("KRW-SOL")

if __name__ == "__main__":
    main()