import pandas as pd

import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote

def file_load() :
    file_path = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_setting.txt"
    data = pd.read_csv(file_path)
    #
    Access_Key = data.loc[data['type'] == 'Access_Key', 'value'].values[0]
    Secret_Key = data.loc[data['type'] == 'Secret_Key', 'value'].values[0]
    #
    os.environ['UPBIT_OPEN_API_ACCESS_KEY'] = Access_Key
    os.environ['UPBIT_OPEN_API_SECRET_KEY'] = Secret_Key
    os.environ['UPBIT_OPEN_API_SERVER_URL'] = 'https://api.upbit.com'
    #
    print(f"Access Key: {Access_Key}")
    print(f"Secret Key: {Secret_Key}")

def Market_Data() :
    # API 요청 URL
    url = "https://api.upbit.com/v1/market/all"

    # GET 요청 보내기
    response = requests.get(url)

    # 응답 상태 코드 확인
    print(f"Status Code: {response.status_code}")

    # 응답 데이터 출력 (JSON 형식으로 파싱)
    if response.status_code == 200:
        data = response.json()  # JSON 응답을 Python 객체로 변환
        df = pd.DataFrame(data)
        return df
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return 0


#특정 종목 마켓 데이터 불러오기
def Market_Data_Specific(ticker) :
    # API 요청 URL
    url = f"https://api.upbit.com/v1/ticker?markets={ticker}"

    # GET 요청 보내기
    response = requests.get(url)

    # 응답 상태 코드 확인
    print(f"Status Code: {response.status_code}")

    # 응답 데이터 출력 (JSON 형식으로 파싱)
    if response.status_code == 200:
        data = response.json()  # JSON 응답을 Python 객체로 변환
        df = pd.DataFrame(data)
        print(df)
    else:
        print(f"Failed to retrieve data: {response.status_code}")

#분봉 데이터 불러오기
def candle(type, ticker, count) :
    # API 요청 URL
    url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&count={count}"

    # GET 요청 보내기
    response = requests.get(url)

    # 응답 상태 코드 확인
    print(f"Status Code: {response.status_code}")

    # 응답 데이터 출력 (JSON 형식으로 파싱)
    if response.status_code == 200:
        data = response.json()  # JSON 응답을 Python 객체로 변환
        df = pd.DataFrame(data)
        print(df)
    else:
        print(f"Failed to retrieve data: {response.status_code}")

#계좌 보유 현황
def hold_account() :
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
        'Authorization': authorization,
    }

    response = requests.get(server_url + '/v1/accounts', headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    return df

def trasaction_history(ticker) :
    url = f"https://api.upbit.com/v1/trades/ticks?market={ticker}&count=50"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    return df

#주문 가능 정보
def order_possible(ticker) :

    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']

    params = {
        'market': ticker
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
        'Authorization': authorization,
    }

    response = requests.get(server_url + '/v1/orders/chance', params=params, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    print(df)

def open_order(ticker) :
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']

    params = {
        'market': ticker,
        'states[]': ['wait', 'watch']
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization = 'Bearer {}'.format(jwt_token)
    headers = {
        'Authorization': authorization,
    }

    response = requests.get(server_url + '/v1/orders/open', params=params, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    print(df)