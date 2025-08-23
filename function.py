# 필요한 라이브러리 임포트
import pandas as pd
import jwt
import hashlib
import os
import requests
import uuid
import json
from urllib.parse import urlencode, unquote, quote

# 전역 변수로 기술적 지표 설정 데이터를 저장할 DataFrame 초기화
feature_data = pd.DataFrame()

# API 키 설정 파일을 로드하는 함수
def file_load(path):
    """
    지정된 경로의 CSV 파일에서 Access Key와 Secret Key를 읽어와 환경 변수에 설정합니다.
    Upbit API 서버 URL도 환경 변수에 설정합니다.
    - path: 설정 파일 경로
    """
    data = pd.read_csv(path)
    Access_Key = data.loc[data['type'] == 'Access_Key', 'value'].values[0]
    Secret_Key = data.loc[data['type'] == 'Secret_Key', 'value'].values[0]
    os.environ['UPBIT_OPEN_API_ACCESS_KEY'] = Access_Key
    os.environ['UPBIT_OPEN_API_SECRET_KEY'] = Secret_Key
    os.environ['UPBIT_OPEN_API_SERVER_URL'] = 'https://api.upbit.com'

# 일반 CSV 파일을 로드하는 함수
def file_load2(path):
    """
    지정된 경로의 CSV 파일을 읽어 DataFrame으로 반환합니다. (주로 과거 데이터 로드용)
    - path: 데이터 파일 경로
    """
    data = pd.read_csv(path)
    return data

# 기술적 지표 설정 파일을 로드하는 함수
def file_load3(path):
    """
    지정된 경로의 CSV 파일에서 기술적 지표 설정을 읽어 전역 변수 `feature_data`에 저장합니다.
    - path: 기술적 지표 설정 파일 경로
    """
    global feature_data
    data = pd.read_csv(path)
    feature_data = pd.DataFrame(data)

# 특정 티커의 호가 정보를 조회하는 함수
def hoga_list(ticker):
    """
    Upbit API를 통해 특정 티커의 현재 호가 정보를 받아와 DataFrame으로 반환합니다.
    - ticker: 조회할 티커 (예: "KRW-XRP")
    """
    url = f"https://api.upbit.com/v1/orderbook?markets={ticker}&level=0"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    orderbook_units = data[0]['orderbook_units']
    df = pd.DataFrame(orderbook_units, columns=['ask_price', 'bid_price'])
    return df

# 거래 가능한 모든 마켓 정보를 조회하는 함수
def Market_Data():
    """
    Upbit API를 통해 거래 가능한 모든 마켓의 정보를 조회합니다.
    - GET /v1/market/all
    """
    url = "https://api.upbit.com/v1/market/all"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return 0

# 특정 티커의 현재가 정보를 조회하는 함수
def Market_Data_Specific(ticker):
    """
    Upbit API를 통해 특정 티커의 현재 Ticker 정보를 조회합니다.
    - GET /v1/ticker
    - ticker: 조회할 티커 (예: "KRW-XRP")
    """
    url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        print(df)
    else:
        print(f"Failed to retrieve data: {response.status_code}")

# 분봉 데이터를 조회하는 함수
def candle(type, ticker, count, time):
    """
    Upbit API를 통해 특정 티커의 분봉 데이터를 조회합니다. (최대 200개)
    - GET /v1/candles/minutes/{unit}
    - type: 분 단위 (1, 3, 5, 10, 15, 30, 60, 240)
    - ticker: 조회할 티커
    - count: 가져올 캔들 개수
    - time: 조회 기준 시각 (ISO 8601 형식), 0일 경우 현재 시각 기준
    """
    if time == 0:
        url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&count={count}"
    else:
        encoded_time = quote(time)
        url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&to={encoded_time}&count={count}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    return df

# 전체 계좌 잔고를 조회하는 함수
def hold_account():
    """
    Upbit API를 통해 현재 보유한 모든 자산의 정보를 조회합니다. (인증 필요)
    - GET /v1/accounts
    """
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    payload = {'access_key': access_key, 'nonce': str(uuid.uuid4())}
    jwt_token = jwt.encode(payload, secret_key)
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}
    response = requests.get(server_url + '/v1/accounts', headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    return df

# 주문 가능 정보를 조회하는 함수
def order_possible(ticker):
    """
    Upbit API를 통해 특정 마켓의 주문 가능 정보를 조회합니다. (인증 필요)
    - GET /v1/orders/chance
    - ticker: 조회할 티커
    """
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker}
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key, 'nonce': str(uuid.uuid4()),
        'query_hash': query_hash, 'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}
    response = requests.get(server_url + '/v1/orders/chance', params=params, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    print(df)

# 주문을 실행하는 함수
def open_order(ticker, type, ord_type, volume, price, ui):
    """
    Upbit API를 통해 지정가 또는 시장가 주문을 실행합니다. (인증 필요)
    - POST /v1/orders
    - ticker: 주문할 티커
    - type: 주문 종류 ('bid': 매수, 'ask': 매도)
    - ord_type: 주문 방식 ('limit': 지정가, 'price': 시장가 매수, 'market': 시장가 매도)
    - volume: 주문 수량 (지정가, 시장가 매도)
    - price: 주문 가격 (지정가, 시장가 매수)
    - ui: 로그 출력을 위한 UI 객체
    """
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {
        'market': ticker, 'side': type, 'ord_type': ord_type,
        'price': price, 'volume': volume
    }
    # 시장가 매수일 경우, 'volume' 파라미터 제거
    if type == 'bid' and ord_type == 'price':
        params = {'market': ticker, 'side': type, 'ord_type': ord_type, 'price': price}
    # 시장가 매도일 경우, 'price' 파라미터 제거
    if type == 'ask' and ord_type == 'market':
        params = {'market': ticker, 'side': type, 'ord_type': ord_type, 'volume': volume}

    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key, 'nonce': str(uuid.uuid4()),
        'query_hash': query_hash, 'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}
    response = requests.post(server_url + '/v1/orders', json=params, headers=headers)
    data = response.json()
    # 주문 결과를 UI 로그에 출력
    ui.textBrowser_2.append('-----ORDER-----')
    ui.textBrowser_2.append(json.dumps(data, indent=4))
    ui.textBrowser_2.append('-----ORDER-----')

# 주문을 취소하는 함수
def close_order(uuid_tmp):
    """
    Upbit API를 통해 특정 주문을 취소합니다. (인증 필요)
    - DELETE /v1/order
    - uuid_tmp: 취소할 주문의 UUID
    """
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'uuid': uuid_tmp}
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key, 'nonce': str(uuid.uuid4()),
        'query_hash': query_hash, 'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}
    response = requests.delete(server_url + '/v1/order', params=params, headers=headers)
    data = response.json()
    # 취소 결과를 콘솔에 출력
    print('-----CANCEL--------------')
    print(data)
    print('-----CANCEL--------------')

# 미체결 주문 내역을 조회하는 함수
def order_wait_history(ticker):
    """
    Upbit API를 통해 특정 마켓의 미체결 주문(wait, watch) 내역을 조회합니다. (인증 필요)
    - GET /v1/orders/open
    - ticker: 조회할 티커
    """
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'states[]': ['wait', 'watch']}
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key, 'nonce': str(uuid.uuid4()),
        'query_hash': query_hash, 'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}
    response = requests.get(server_url + '/v1/orders/open', params=params, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    return df

# 완료 또는 취소된 주문 내역을 조회하는 함수
def order_close_history(ticker, time):
    """
    Upbit API를 통해 특정 마켓의 완료(done) 또는 취소(cancel)된 주문 내역을 조회합니다. (인증 필요)
    - GET /v1/orders/closed
    - ticker: 조회할 티커
    - time: 조회 종료 시각 (ISO 8601 형식)
    """
    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'states[]': ['done', 'cancel'], 'end_time': time}
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()
    payload = {
        'access_key': access_key, 'nonce': str(uuid.uuid4()),
        'query_hash': query_hash, 'query_hash_alg': 'SHA512',
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization = f'Bearer {jwt_token}'
    headers = {'Authorization': authorization}
    response = requests.get(server_url + '/v1/orders/closed', params=params, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    return df
