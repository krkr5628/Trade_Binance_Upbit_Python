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
import function_feature
import function_complex

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
from PySide6.QtGui import QStandardItemModel, QStandardItem

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

file_path1 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_setting.txt" #setting
file_path2 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\Goole Drive\\Data\\SOL_Data_Test_1m_Recent_Indicator3_essential.csv" #data
file_path3 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_feature_setting.txt" #setting-feature
file_path4 = "" #model
ticker = "KRW-XRP"
candle_row = 216000 #43200, 86400, 129600, 172800, 216000, 259200, 302400

def main():

    #초기 윈도우 생성
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    # Ui_MainWindow 인스턴스 생성
    ui = Ui_MainWindow()
    ui.setupUi(main_window)  # QMainWindow에 UI 설정

    # API KEYS LOAD
    function.file_load(file_path1)  # API KEYS LOAD

    # Feature Settomg LOAD
    #function.file_load(file_path3)

    # Feature Matching
    function_feature.feature_inital_match()
    #function_feature.feature_match()

    # setting initial
    function_complex.setting_initial(ui)

    #계좌 + 청산 업데이트
    function_complex.Account(ui, ticker)

    # 주문 완료 및 취소 항목(1시간 이내)
    function_complex.Order_Complete(ui, ticker)

    #주문 대기 및 예약 항목 + 취소 버튼
    function_complex.Order_Wait(ui, ticker)

    #초기 데이터 로딩
    function_complex.Candle_initial_update(ui, ticker, file_path2)

    #초기 분봉 업데이트
    #function_complex.Candle_initial(ui, ticker)

    # 시간 표시 및 시간 관련 이벤트 처리
    def showTime():

        # 현재 시각 가져오기
        time = QDateTime.currentDateTime()
        ui.lcdNumber.display(time.toString('yyyy-MM-dd HH:mm:ss'))

        # 분봉 업데이트(1분 주기)
        if time.time().second() == 5:
           function_complex.Candle_update(time, ticker, ui)

        #예측

    # 타이머 생성
    timer = QTimer()
    timer.timeout.connect(showTime)
    timer.start(1000)

    # Refresh 버튼
    def refresh():
        function_complex.Account(ui, ticker)
        function_complex.Order_Wait(ui, ticker)
        function_complex.Order_Complete(ui, ticker)
    ui.pushButton_8.clicked.connect(refresh)

    #매수 주문 버튼
    def order() :

        #시장가 => 매수할 총 금액 입력, 지정가 => 호가 입력
        price_volume_order = ui.textEdit_2.toPlainText()

        #입력값이 없으면 경고
        if not price_volume_order.strip():  # strip()으로 공백만 있는 경우도 체크
            ui.textBrowser_2.append("[경고] 매수 금액 입력")
            return

        #매수 매도 5천원 넘지 않으면 경고

        #주문 타입 확인
        ord_type = 'limit'
        ord_type_hoga = ui.comboBox.currentText()
        if ord_type_hoga == 'Market' :
            ord_type_hoga = 0
            ord_type = 'price'
        else :
            # 호가 계산
            ord_type_hoga = function_complex.hoga(ticker, ord_type_hoga)

        #open_order(ticker, type, ord_type, volume, price, ui)
        function.open_order(ticker, 'bid', ord_type, ord_type_hoga, price_volume_order, ui)
        refresh()

    ui.pushButton_11.clicked.connect(order)

    # 메인 윈도우 보여주기 및 애플리케이션 실행
    main_window.show()

    # 비동기 시세 처리
    loop = QEventLoop(app)
    loop.create_task(function_real.web_socket_initial(ui))
    loop.run_forever()


if __name__ == "__main__":
    main()