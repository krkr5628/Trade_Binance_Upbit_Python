import jwt  # PyJWT
import uuid
import websockets   # websocket-client
import os
import json
import function_complex

async def web_socket_initial(ui):
    async def on_message(ws):
        async for message in ws:
            # 서버로부터 메시지를 수신했을 때 호출
            # 수신된 메시지는 UTF-8로 디코딩
            data = message.decode('utf-8')
            # JSON 데이터를 파싱
            json_data = json.loads(data)
            # trade_price 값 추출
            trade_price = json_data.get("trade_price", "No trade_price found")
            #글로벌 변수
            avg_price = function_complex.avg_price
            #상승 하락 차이
            price_difference_percentage = 0
            if not avg_price == 0 :
                price_difference_percentage = round((float(trade_price) - float(avg_price)) / float(avg_price) * 100, 3)
            # UI 업데이트 - 받은 메시지를 textBrowser_4에 출력
            ui.textBrowser_4.setText(f"{str(trade_price)} / {avg_price} / {price_difference_percentage}%")

    async def on_connect(ws):
        # WebSocket 서버에 성공적으로 연결되었을 때 호출
        print("connected!")
        await ws.send('[{"ticket":"UNIQUE_TICKET"},{"type":"ticker", "codes":["KRW-XRP"], "isOnlyRealtime" : "True"}]')

    async def on_error(ws, err):
        # WebSocket 통신 중에 에러가 발생했을 때 호출
        print(err)

    async def on_close(ws):
        # WebSocket 연결이 종료되었을 때 호출
        print("closed!")

    access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
    secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorization_token = f'Bearer {jwt_token}'
    headers = {"Authorization": authorization_token}

    uri = "wss://api.upbit.com/websocket/v1"

    async with websockets.connect(uri, extra_headers=headers) as ws:
        await on_connect(ws)
        try:
            await on_message(ws)
        except websockets.ConnectionClosed as e:
            await on_close(ws)
        except Exception as e:
            await on_error(ws, e)