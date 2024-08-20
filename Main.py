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

import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import pandas as pd

Access_Key = ""
Secret_Key = ""

def file_load() :
    file_path = "C:\\Users\\krkr5\\OneDrive\\바탕 화면\\project\\password\\upbit_setting.txt"
    data = pd.read_csv(file_path)
    Access_Key = data.loc[data['type'] == 'Access_Key', 'value'].values[0]
    Secret_Key = data.loc[data['type'] == 'Secret_Key', 'value'].values[0]
    print(f"Access Key: {Access_Key}")
    print(f"Secret Key: {Secret_Key}")

#파라미터가 없는 경우
def Authorization() :
    payload = {
        'access_key': Access_Key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, Secret_Key)
    authorization_token = 'Bearer {}'.format(jwt_token)

#파라미터가 있는 경우(query => 파라미터의 자료형 중 배열이 존재하는 경우)
def Authorization(parms) :
    query = {
        #"key[]": ["value1", "value2", "value3"]  # 파라미터의 자료형 중 배열이 존재하는 경우
        "key[]": parms # 파라미터의 자료형 중 배열이 존재하는 경우
    }

    m = hashlib.sha512()
    m.update(urlencode(query).encode())
    query_hash = m.hexdigest()

    payload = {
        'access_key': Access_Key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, Secret_Key)
    authorization_token = 'Bearer {}'.format(jwt_token)

def main():
    file_load()

if __name__ == "__main__":
    main()