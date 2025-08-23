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

# 필요한 모듈 임포트
import function  # API 관련 함수 모음
import function_real  # 실시간 웹소켓 관련 함수 모음
import function_feature  # 기술적 지표 계산 함수 모음
import function_complex  # 복합적인 기능 및 UI 연동 함수 모음

import pandas as pd
import numpy as np
from datetime import datetime
import time
import asyncio

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtCore import QAbstractTableModel, Qt, QTimer, QDateTime
from Main_ui import Ui_MainWindow  # UI 레이아웃
from qasync import QEventLoop  # Qt와 asyncio를 함께 사용하기 위한 이벤트 루프
from PySide6.QtGui import QStandardItemModel, QStandardItem

import tkinter as tk
from tkinter import ttk

# 머신러닝 모델을 위한 scikit-learn 라이브러리
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

# API 인증 및 요청을 위한 라이브러리
import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote

# 파일 경로 설정
file_path1 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_setting.txt" # API 설정 파일
file_path2 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\Goole Drive\\Data\\SOL_Data_Test_1m_Recent_Indicator3_essential.csv" # 과거 데이터 파일
file_path3 = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_feature_setting.txt" # 기술적 지표 설정 파일
file_path4 = "" # 학습된 모델 파일 경로 (현재 비어있음)
ticker = "KRW-XRP"  # 거래할 코인 티커
candle_row = 216000 # 캔들 데이터 행 수 (현재 사용되지 않음)

# 메인 실행 함수
def main():

    # PyQt6 애플리케이션 생성
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    # UI 클래스 인스턴스화 및 메인 윈도우에 UI 설정
    ui = Ui_MainWindow()
    ui.setupUi(main_window)

    # API 키 로드
    function.file_load(file_path1)

    # 기술적 지표 설정 로드 (현재 주석 처리됨)
    #function.file_load(file_path3)

    # 기술적 지표 초기 설정
    function_feature.feature_inital_match()
    #function_feature.feature_match() # 사용자 설정에 따른 매칭 (현재 주석 처리됨)

    # UI 초기 설정 (콤보박스 등)
    function_complex.setting_initial(ui)

    # 계좌 정보 및 보유 자산 표시
    function_complex.Account(ui, ticker)

    # 최근 1시간 동안의 완료/취소된 주문 내역 표시
    function_complex.Order_Complete(ui, ticker)

    # 현재 대기 중인 주문 내역 표시
    function_complex.Order_Wait(ui, ticker)

    # 로컬 CSV 파일 및 API를 통해 초기 캔들 데이터 로딩 및 표시
    function_complex.Candle_initial_update(ui, ticker, file_path2)

    # API를 통해서만 초기 캔들 데이터 로딩 (현재 주석 처리됨)
    #function_complex.Candle_initial(ui, ticker)

    # 시간 표시 및 주기적 업데이트를 위한 내부 함수
    def showTime():

        # 현재 시간을 가져와 UI의 LCD 위젯에 표시
        time = QDateTime.currentDateTime()
        ui.lcdNumber.display(time.toString('yyyy-MM-dd HH:mm:ss'))

        # 매 분 5초마다 캔들 데이터 업데이트
        if time.time().second() == 5:
            function_complex.Candle_update(time, ticker, ui)

            # 예측 기능 (더미 모델 사용)
            # 최신 특성 데이터를 가져와 예측 함수에 전달
            if 'candle_df_features' in function_complex.__dict__ and not function_complex.candle_df_features.empty:
                latest_features = function_complex.candle_df_features.tail(1)
                prediction = function_feature.get_prediction(latest_features)
                # UI의 label_4에 예측 결과 표시
                ui.label_4.setText(f"AI 예측: {prediction}")

    # 1초마다 showTime 함수를 호출하는 타이머 설정
    timer = QTimer()
    timer.timeout.connect(showTime)
    timer.start(1000)

    # 'REFRESH' 버튼 클릭 시 호출될 내부 함수
    def refresh():
        # 계좌, 대기 주문, 완료 주문 정보를 새로고침
        function_complex.Account(ui, ticker)
        function_complex.Order_Wait(ui, ticker)
        function_complex.Order_Complete(ui, ticker)
    # UI의 'pushButton_8' (REFRESH 버튼)에 refresh 함수 연결
    ui.pushButton_8.clicked.connect(refresh)

    # 'ORDER' 버튼 클릭 시 호출될 내부 함수
    def order():
        """
        UI에서 입력된 정보를 바탕으로 매수 주문을 실행합니다.
        - 지정가/시장가 주문 유형을 처리합니다.
        - 최소 주문 금액(5,000원)을 확인합니다.
        - 입력값 유효성을 검사합니다.
        """
        price_volume_input = ui.textEdit_2.toPlainText()

        # 입력값 유효성 검사
        if not price_volume_input.strip():
            ui.textBrowser_2.append("[경고] 주문 금액 또는 수량을 입력해주세요.")
            return
        try:
            price_volume_value = float(price_volume_input)
        except ValueError:
            ui.textBrowser_2.append("[에러] 주문 입력값은 숫자여야 합니다.")
            return

        # 주문 파라미터 초기화
        order_price = '0'
        order_volume = '0'
        selected_ord_type = ui.comboBox.currentText()

        # 주문 유형에 따라 파라미터 설정 및 유효성 검사
        if selected_ord_type == 'Market':
            ord_type = 'price'  # 시장가 매수
            order_price = price_volume_input  # 시장가 매수 시에는 주문 총액을 price로 전달
            # 최소 주문 금액 체크
            if price_volume_value < 5000:
                ui.textBrowser_2.append("[경고] 최소 주문 금액은 5,000원입니다.")
                return
        else:
            ord_type = 'limit'  # 지정가
            order_volume = price_volume_input  # 지정가 시에는 주문 수량을 volume으로 전달
            # 지정가 가격 조회
            hoga_price = function_complex.hoga(ticker, selected_ord_type)
            if hoga_price is None:
                ui.textBrowser_2.append(f"[에러] 호가({selected_ord_type}) 조회에 실패하여 주문을 중단합니다.")
                return
            order_price = str(hoga_price)
            # 최소 주문 금액 체크
            if price_volume_value * hoga_price < 5000:
                ui.textBrowser_2.append(f"[경고] 최소 주문 금액(5,000원) 미만입니다. (현재 주문액: {price_volume_value * hoga_price:,.0f}원)")
                return

        # 주문 실행
        ui.textBrowser_2.append(f"주문 실행: {ticker} / {ord_type} / 가격:{order_price} / 수량:{order_volume}")
        function.open_order(ticker, 'bid', ord_type, order_volume, order_price, ui)

        # 주문 후 정보 새로고침
        refresh()

    # UI의 'pushButton_11' (ORDER 버튼)에 order 함수 연결
    ui.pushButton_11.clicked.connect(order)

    # 메인 윈도우 표시
    main_window.show()

    # 비동기 웹소켓 처리를 위한 이벤트 루프 설정
    loop = QEventLoop(app)
    # 웹소켓 연결 및 실시간 시세 수신 시작
    loop.create_task(function_real.web_socket_initial(ui))
    # 이벤트 루프 실행
    loop.run_forever()


# 이 스크립트가 직접 실행될 때 main 함수 호출
if __name__ == "__main__":
    main()