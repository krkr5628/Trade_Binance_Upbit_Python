# 필요한 라이브러리 임포트
import jwt          # PyJWT, JWT 토큰 생성 및 검증
import uuid         # 고유 식별자 생성
import websockets   # 비동기 웹소켓 클라이언트
import os           # 환경 변수 접근
import json         # JSON 데이터 파싱
import function_complex # 다른 모듈의 변수(avg_price) 접근

# Upbit 웹소켓에 연결하고 실시간 데이터를 수신하는 메인 비동기 함수
async def web_socket_initial(ui):
    """
    Upbit의 웹소켓 서버에 연결하여 실시간 시세 데이터를 받아 UI에 업데이트합니다.
    - JWT 토큰을 생성하여 인증합니다.
    - 연결 성공 시, 특정 티커에 대한 구독 메시지를 전송합니다.
    - 메시지 수신 시, 데이터를 파싱하여 UI의 텍스트 브라우저를 업데이트합니다.
    - ui: 업데이트할 PySide6 UI 객체
    """

    # 웹소켓 메시지 수신 시 호출될 내부 비동기 함수
    async def on_message(ws):
        """
        서버로부터 메시지를 지속적으로 수신하고 처리합니다.
        """
        async for message in ws:
            # 수신된 메시지(바이트)를 UTF-8 문자열로 디코딩
            data = message.decode('utf-8')
            # JSON 형식의 문자열을 파이썬 딕셔너리로 파싱
            json_data = json.loads(data)
            # 'trade_price' (현재가) 값을 추출
            trade_price = json_data.get("trade_price", "N/A")

            # function_complex 모듈의 전역 변수 'avg_price' (평균 매수 단가) 가져오기
            avg_price = function_complex.avg_price

            # 평균 매수 단가 대비 현재가의 등락률 계산
            price_difference_percentage = 0
            if avg_price != 0 and trade_price != "N/A":
                try:
                    price_difference_percentage = round((float(trade_price) - float(avg_price)) / float(avg_price) * 100, 3)
                except ValueError:
                    price_difference_percentage = 0 # 가격 정보가 숫자가 아닐 경우 예외 처리

            # UI의 textBrowser_4에 현재가, 평균 매수 단가, 등락률을 표시
            ui.textBrowser_4.setText(f"{str(trade_price)} / {avg_price} / {price_difference_percentage}%")

    # 웹소켓 연결 성공 시 호출될 내부 비동기 함수
    async def on_connect(ws):
        """
        웹소켓 연결이 성공적으로 이루어졌을 때, 구독 메시지를 전송합니다.
        """
        print("WebSocket connected!")
        # 구독할 내용을 JSON 형식으로 만들어 서버에 전송
        # ticket: 고유 식별자, type: 구독 종류(ticker), codes: 티커 목록
        await ws.send('[{"ticket":"UNIQUE_TICKET"},{"type":"ticker", "codes":["KRW-XRP"], "isOnlyRealtime" : "True"}]')

    # 웹소켓 에러 발생 시 호출될 내부 비동기 함수
    async def on_error(ws, err):
        """
        웹소켓 통신 중 에러가 발생했을 때 호출됩니다.
        """
        print(f"WebSocket error: {err}")

    # 웹소켓 연결 종료 시 호출될 내부 비동기 함수
    async def on_close(ws, code, reason):
        """
        웹소켓 연결이 종료되었을 때 호출됩니다.
        """
        print(f"WebSocket closed! Code: {code}, Reason: {reason}")

    # 웹소켓 인증을 위한 JWT 토큰 생성
    access_key = os.environ.get('UPBIT_OPEN_API_ACCESS_KEY')
    secret_key = os.environ.get('UPBIT_OPEN_API_SECRET_KEY')

    # 키가 없는 경우 함수 종료
    if not access_key or not secret_key:
        print("API keys are not set in environment variables.")
        return

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }
    jwt_token = jwt.encode(payload, secret_key)
    authorization_token = f'Bearer {jwt_token}'
    headers = {"Authorization": authorization_token}

    # Upbit 웹소켓 서버 주소
    uri = "wss://api.upbit.com/websocket/v1"

    # 웹소켓 서버에 연결 및 통신 시작
    while True: # 재연결 로직을 위해 while 루프 사용
        try:
            async with websockets.connect(uri, extra_headers=headers) as ws:
                await on_connect(ws)
                await on_message(ws)
        except websockets.exceptions.ConnectionClosed as e:
            await on_close(ws, e.code, e.reason)
        except Exception as e:
            # on_error는 ws 객체가 필요하므로, 여기서는 직접 에러를 출력
            print(f"An unexpected error occurred: {e}")

        # 재연결 시도 전 잠시 대기
        print("Attempting to reconnect in 5 seconds...")
        await asyncio.sleep(5)