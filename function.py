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
    try:
        data = pd.read_csv(path)
        Access_Key = data.loc[data['type'] == 'Access_Key', 'value'].values[0]
        Secret_Key = data.loc[data['type'] == 'Secret_Key', 'value'].values[0]
        os.environ['UPBIT_OPEN_API_ACCESS_KEY'] = Access_Key
        os.environ['UPBIT_OPEN_API_SECRET_KEY'] = Secret_Key
        os.environ['UPBIT_OPEN_API_SERVER_URL'] = 'https://api.upbit.com'
    except FileNotFoundError:
        print(f"[ERROR] 설정 파일을 찾을 수 없습니다: {path}")
    except Exception as e:
        print(f"[ERROR] 설정 파일 로드 중 오류 발생: {e}")

# 일반 CSV 파일을 로드하는 함수
def file_load2(path):
    """
    지정된 경로의 CSV 파일을 읽어 DataFrame으로 반환합니다. (주로 과거 데이터 로드용)
    - path: 데이터 파일 경로
    """
    try:
        data = pd.read_csv(path)
        return data
    except FileNotFoundError:
        print(f"[ERROR] 데이터 파일을 찾을 수 없습니다: {path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] 데이터 파일 로드 중 오류 발생: {e}")
        return pd.DataFrame()

# 기술적 지표 설정 파일을 로드하는 함수
def file_load3(path):
    """
    지정된 경로의 CSV 파일에서 기술적 지표 설정을 읽어 전역 변수 `feature_data`에 저장합니다.
    - path: 기술적 지표 설정 파일 경로
    """
    global feature_data
    try:
        data = pd.read_csv(path)
        feature_data = pd.DataFrame(data)
    except FileNotFoundError:
        print(f"[ERROR] 지표 설정 파일을 찾을 수 없습니다: {path}")
    except Exception as e:
        print(f"[ERROR] 지표 설정 파일 로드 중 오류 발생: {e}")

# 특정 티커의 호가 정보를 조회하는 함수
def hoga_list(ticker):
    """
    Upbit API를 통해 특정 티커의 현재 호가 정보를 받아와 DataFrame으로 반환합니다.
    - ticker: 조회할 티커 (예: "KRW-XRP")
    """
    url = f"https://api.upbit.com/v1/orderbook?markets={ticker}&level=0"
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 2xx 응답이 아닐 경우 예외 발생
        data = response.json()
        orderbook_units = data[0]['orderbook_units']
        df = pd.DataFrame(orderbook_units, columns=['ask_price', 'bid_price'])
        return df
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] 호가 정보 조회 실패: {e}")
        return pd.DataFrame()
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[API ERROR] 호가 정보 파싱 실패: {e}")
        return pd.DataFrame()

# 거래 가능한 모든 마켓 정보를 조회하는 함수
def Market_Data():
    """
    Upbit API를 통해 거래 가능한 모든 마켓의 정보를 조회합니다.
    - GET /v1/market/all
    """
    url = "https://api.upbit.com/v1/market/all"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] 전체 마켓 정보 조회 실패: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"[API ERROR] 전체 마켓 정보 파싱 실패: {e}")
        return pd.DataFrame()

# 특정 티커의 현재가 정보를 조회하는 함수
def Market_Data_Specific(ticker):
    """
    Upbit API를 통해 특정 티커의 현재 Ticker 정보를 조회합니다.
    - GET /v1/ticker
    - ticker: 조회할 티커 (예: "KRW-XRP")
    """
    url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] 특정 마켓({ticker}) 정보 조회 실패: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"[API ERROR] 특정 마켓({ticker}) 정보 파싱 실패: {e}")
        return pd.DataFrame()

# 분봉 데이터를 조회하는 함수
def candle(type, ticker, count, time):
    """
    Upbit API를 통해 특정 티커의 분봉 데이터를 조회합니다. (최대 200개)
    - GET /v1/candles/minutes/{unit}
    """
    if time == 0:
        url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&count={count}"
    else:
        encoded_time = quote(time)
        url = f"https://api.upbit.com/v1/candles/minutes/{type}?market={ticker}&to={encoded_time}&count={count}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        print(f"[API ERROR] 캔들 데이터 조회 실패: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"[API ERROR] 캔들 데이터 파싱 실패: {e}")
        return pd.DataFrame()

# API 요청을 위한 공통 인증 헤더 생성 함수
def _get_auth_headers(query_params=None):
    """
    API 인증을 위한 JWT 헤더를 생성합니다.
    - query_params: 쿼리 파라미터가 있는 경우, 해싱을 위해 전달
    """
    access_key = os.environ.get('UPBIT_OPEN_API_ACCESS_KEY')
    secret_key = os.environ.get('UPBIT_OPEN_API_SECRET_KEY')
    if not access_key or not secret_key:
        raise ValueError("API 키가 환경 변수에 설정되지 않았습니다.")

    payload = {'access_key': access_key, 'nonce': str(uuid.uuid4())}

    if query_params:
        query_string = unquote(urlencode(query_params, doseq=True)).encode("utf-8")
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()
        payload['query_hash'] = query_hash
        payload['query_hash_alg'] = 'SHA512'

    jwt_token = jwt.encode(payload, secret_key)
    return {'Authorization': f'Bearer {jwt_token}'}

# 전체 계좌 잔고를 조회하는 함수
def hold_account():
    """
    Upbit API를 통해 현재 보유한 모든 자산의 정보를 조회합니다. (인증 필요)
    - GET /v1/accounts
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    try:
        headers = _get_auth_headers()
        response = requests.get(server_url + '/v1/accounts', headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] 계좌 조회 실패: {e}")
        return pd.DataFrame()

# 주문 가능 정보를 조회하는 함수
def order_possible(ticker):
    """
    Upbit API를 통해 특정 마켓의 주문 가능 정보를 조회합니다. (인증 필요)
    - GET /v1/orders/chance
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker}
    try:
        headers = _get_auth_headers(params)
        response = requests.get(server_url + '/v1/orders/chance', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] 주문 가능 정보 조회 실패: {e}")
        return pd.DataFrame()

# 주문을 실행하는 함수
def open_order(ticker, type, ord_type, volume, price, ui):
    """
    Upbit API를 통해 지정가 또는 시장가 주문을 실행합니다. (인증 필요)
    - POST /v1/orders
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'side': type, 'ord_type': ord_type}

    if ord_type == 'price': # 시장가 매수
        params['price'] = price
    elif ord_type == 'market': # 시장가 매도
        params['volume'] = volume
    else: # 지정가
        params['volume'] = volume
        params['price'] = price

    try:
        headers = _get_auth_headers(params)
        response = requests.post(server_url + '/v1/orders', json=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        ui.textBrowser_2.append('-----ORDER SUCCESS-----')
        ui.textBrowser_2.append(json.dumps(data, indent=4))
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] 주문 실패: {e}")
        ui.textBrowser_2.append('-----ORDER FAILED-----')
        ui.textBrowser_2.append(str(e))
    finally:
        ui.textBrowser_2.append('--------------------')


# 주문을 취소하는 함수
def close_order(uuid_tmp):
    """
    Upbit API를 통해 특정 주문을 취소합니다. (인증 필요)
    - DELETE /v1/order
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'uuid': uuid_tmp}
    try:
        headers = _get_auth_headers(params)
        response = requests.delete(server_url + '/v1/order', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        print('-----CANCEL SUCCESS-----')
        print(data)
        return data
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"-----CANCEL FAILED-----: {e}")
        return None

# 미체결 주문 내역을 조회하는 함수
def order_wait_history(ticker):
    """
    Upbit API를 통해 특정 마켓의 미체결 주문(wait, watch) 내역을 조회합니다. (인증 필요)
    - GET /v1/orders/open
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'states[]': ['wait', 'watch']}
    try:
        headers = _get_auth_headers(params)
        response = requests.get(server_url + '/v1/orders/open', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] 미체결 주문 조회 실패: {e}")
        return pd.DataFrame()

# 완료 또는 취소된 주문 내역을 조회하는 함수
def order_close_history(ticker, time):
    """
    Upbit API를 통해 특정 마켓의 완료(done) 또는 취소(cancel)된 주문 내역을 조회합니다. (인증 필요)
    - GET /v1/orders/closed
    """
    server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']
    params = {'market': ticker, 'states[]': ['done', 'cancel'], 'end_time': time}
    try:
        headers = _get_auth_headers(params)
        response = requests.get(server_url + '/v1/orders/closed', params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        print(f"[API ERROR] 완료/취소 주문 조회 실패: {e}")
        return pd.DataFrame()
