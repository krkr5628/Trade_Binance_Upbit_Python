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

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
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

def window_ticker() :
    # 루트 창 생성
    root = tk.Tk()

    # 창의 제목 설정
    root.title("TICKER LIST")

    #TICKER_TOTAL
    rst_df = function.Market_Data()  # TOTAL TICKER

    if rst_df != 0 :
        # 내부 프레임 생성
        frame = tk.Frame(root)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Treeview 위젯 생성 및 프레임에 배치
        tree = ttk.Treeview(frame)
        tree.pack(expand=True, fill='both')

        tree["columns"] = list(rst_df.columns)
        tree["show"] = "headings"

        for col in rst_df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 기존 데이터 삭제
        for row in tree.get_children():
            tree.delete(row)

        # 새로운 데이터 삽입
        for index, row in rst_df.iterrows():
            tree.insert("", "end", values=list(row))

    #TICKER_DETAIL
    #function.Market_Data_Specific("KRW-SOL")  # SPECFIC TIKCER INFO

def main():
    function.file_load() #API KEYS LOAD
    #
    app = QApplication(sys.argv)

    # QMainWindow 인스턴스 생성
    main_window = QMainWindow()

    # Ui_MainWindow 인스턴스 생성
    ui = Ui_MainWindow()
    ui.setupUi(main_window)  # QMainWindow에 UI 설정

    # 메인 윈도우 보여주기
    main_window.show()

    # 애플리케이션 실행
    sys.exit(app.exec())

    #
    #function.candle(1,"KRW-BTC",5) #CANDLE
    #function.order_possible("KRW-SOL")
    #function.open_order("KRW-SOL")
    #function.closed_order("KRW-SOL")

if __name__ == "__main__":
    main()