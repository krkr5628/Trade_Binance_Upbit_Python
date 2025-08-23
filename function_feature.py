# 'ta' 라이브러리 (Technical Analysis)와 pandas 임포트
import ta
import pandas as pd

# 'function' 모듈 임포트 (현재 코드에서는 직접 사용되지 않음)
import function

# 사용자가 선택한 지표 설정을 저장할 리스트 (현재 사용되지 않음)
feature_simple = []

# 각 기술적 지표의 계산 주기를 저장할 전역 리스트들
atr_periods = []
stoch_periods = []
bollinger_periods = []
ichimoku_periods = []
supertrend_settings = []
parabolic_sar_settings = []
williams_r_periods = []
momentum_periods = []
roc_periods = []
cmo_periods = []
mfi_periods = []
rsi_periods = []
efi_periods = []
rvi_periods = []
vr_periods = []
cci_periods = []
disparity_periods = []
moving_average_periods = []

# 기술적 지표 계산을 위한 기본 파라미터들을 설정하는 함수
def feature_inital_match():
    """
    각 기술적 지표 계산에 사용될 기본 주기(period)와 설정값들을 전역 리스트에 초기화합니다.
    이 함수는 프로그램 시작 시 한 번 호출되어야 합니다.
    """
    global atr_periods, stoch_periods, bollinger_periods, ichimoku_periods, supertrend_settings
    global parabolic_sar_settings, williams_r_periods, momentum_periods, roc_periods, cmo_periods
    global mfi_periods, rsi_periods, efi_periods, rvi_periods, vr_periods, cci_periods
    global disparity_periods, moving_average_periods

    # 각 지표별로 다양한 주기를 설정하여 여러 버전의 지표를 생성
    atr_periods = [5, 10, 14, 20, 50]
    stoch_periods = [(14, 3), (21, 5), (9, 3), (5, 2), (20, 7)]
    bollinger_periods = [10, 20, 50, 100, 200]
    ichimoku_periods = [9, 26, 52, 100, 200]
    supertrend_settings = [(7, 3, 14), (10, 3, 20), (14, 2, 10), (20, 4, 50), (50, 5, 5)]
    parabolic_sar_settings = [(0.02, 0.2), (0.04, 0.2), (0.06, 0.2), (0.08, 0.2), (0.1, 0.2)]
    williams_r_periods = [10, 20, 30, 40, 50]
    momentum_periods = [10, 20, 30, 40, 50]
    roc_periods = [10, 20, 30, 40, 50]
    cmo_periods = [10, 20, 30, 40, 50]
    mfi_periods = [10, 20, 30, 40, 50]
    rsi_periods = [10, 20, 30, 40, 50]
    efi_periods = [2, 13, 5, 10, 25]
    rvi_periods = [10, 20, 30, 40, 50]
    vr_periods = [10, 20, 30, 40, 50]
    cci_periods = [10, 20, 30, 40, 50]
    disparity_periods = [5, 10, 20, 50, 100, 200]
    moving_average_periods = [5, 10, 20, 50, 100, 200]

# 사용자가 설정 파일에서 선택한 지표만 사용하도록 파라미터를 필터링하는 함수 (현재 미구현)
def feature_match():
    """
    'function.feature_data' (설정 파일에서 로드)를 기반으로
    계산할 기술적 지표의 파라미터를 필터링합니다. (현재는 구현되지 않았습니다.)
    """
    global feature_simple, atr_periods, stoch_periods # ... 등 모든 전역 변수

    # feature_data DataFrame을 반복하며 사용자가 선택한(apply) 지표의 설정값만 가져옴
    for _, feature in function.feature_data.iterrows():
        # 이 부분은 실제 구현이 필요합니다.
        pass

# 주어진 데이터프레임에 모든 기술적 지표를 계산하여 추가하는 메인 함수
def data_feature_1(data):
    """
    입력된 OHLCV 데이터프레임에 정의된 모든 기술적 지표를 계산하여 열로 추가합니다.
    - data: 'open', 'high', 'low', 'close', 'volume' 열을 포함하는 pandas DataFrame
    - 반환값: 기술적 지표들이 추가된 DataFrame
    """

    # --- 각 기술적 지표를 계산하는 내부 헬퍼 함수들 ---

    def calculate_atr(df, periods):
        for period in periods:
            df[f'atr_{period}'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=period)
        return df

    def calculate_vwap(df):
        df['vwap'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'])
        return df

    def calculate_stoch(df, periods):
        for period, smooth in periods:
            df[f'stoch_%k_{period}_{smooth}'] = ta.momentum.stoch(df['high'], df['low'], df['close'], window=period, smooth_window=smooth)
            df[f'stoch_%d_{period}_{smooth}'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'], window=period, smooth_window=smooth)
        return df

    def calculate_obv(df):
        df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        return df

    def calculate_bollinger_bands(df, periods):
        for period in periods:
            bollinger = ta.volatility.BollingerBands(df['close'], window=period)
            df[f'bollinger_hband_{period}'] = bollinger.bollinger_hband()
            df[f'bollinger_lband_{period}'] = bollinger.bollinger_lband()
        return df

    def calculate_ichimoku(df, periods):
        for period in periods:
            df[f'ichimoku_base_{period}'] = ta.trend.ichimoku_base_line(df['high'], df['low'], window1=period)
            df[f'ichimoku_conversion_{period}'] = ta.trend.ichimoku_conversion_line(df['high'], df['low'], window1=period)
        return df

    def calculate_supertrend(df, settings):
        # 'ta' 라이브러리에 슈퍼트렌드가 없으므로 직접 구현
        df = df.copy()
        for period, multiplier, atr_period in settings:
            hl2 = (df['high'] + df['low']) / 2
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)
            df['upperband'] = hl2 + (multiplier * df['atr'])
            df['lowerband'] = hl2 - (multiplier * df['atr'])
            df['in_uptrend'] = True
            for current in range(1, len(df.index)):
                previous = current - 1
                if df['close'].iloc[current] > df['upperband'].iloc[previous]:
                    df.loc[df.index[current], 'in_uptrend'] = True
                elif df['close'].iloc[current] < df['lowerband'].iloc[previous]:
                    df.loc[df.index[current], 'in_uptrend'] = False
                else:
                    df.loc[df.index[current], 'in_uptrend'] = df['in_uptrend'].iloc[previous]
                    if df['in_uptrend'].iloc[current] and df['lowerband'].iloc[current] < df['lowerband'].iloc[previous]:
                        df.loc[df.index[current], 'lowerband'] = df['lowerband'].iloc[previous]
                    if not df['in_uptrend'].iloc[current] and df['upperband'].iloc[current] > df['upperband'].iloc[previous]:
                        df.loc[df.index[current], 'upperband'] = df['upperband'].iloc[previous]
            df[f'supertrend_upper_{period}_{multiplier}_{atr_period}'] = df['upperband']
            df[f'supertrend_lower_{period}_{multiplier}_{atr_period}'] = df['lowerband']
            df[f'supertrend_in_uptrend_{period}_{multiplier}_{atr_period}'] = df['in_uptrend']
        return df

    def calculate_parabolic_sar(df, settings):
        for af, max_af in settings:
            key = f'Parabolic_SAR_{af}'
            df[key] = ta.psar(df['high'], df['low'], df['close'], af=af, max_af=max_af)[f'PSARl_{af}_{max_af}']
        return df

    def calculate_williams_r(df, periods):
        for period in periods:
            df[f'Williams_%R_{period}'] = ta.willr(df['high'], df['low'], df['close'], length=period)
        return df

    def calculate_momentum(df, periods):
        for period in periods:
            df[f'Momentum_{period}'] = ta.mom(df['close'], length=period)
        return df

    def calculate_roc(df, periods):
        for period in periods:
            df[f'ROC_{period}'] = ta.roc(df['close'], length=period)
        return df

    def calculate_cmo(df, periods):
        for period in periods:
            df[f'CMO_{period}'] = ta.cmo(df['close'], length=period)
        return df

    def calculate_mfi(df, periods):
        for period in periods:
            df[f'MFI_{period}'] = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=period)
        return df

f'RSI_{period}'] = ta.rsi(df['close'], length=period)
        return df

    def calculate_ad_line(df):
        df['Accumulation_Distribution_Line'] = ta.ad(df['high'], df['low'], df['close'], df['volume'])
        return df

    def calculate_efi(df, periods):
        for period in periods:
            df[f'Elder_Force_Index_{period}'] = ta.efi(df['close'], df['volume'], length=period)
        return df

    def calculate_rvi(df, periods):
        for period in periods:
            # 경고: 'ta' 라이브러리에는 RVI(Relative Vigor Index)가 내장되어 있지 않습니다.
            # 아래 코드는 임시방편으로 RSI를 사용하고 있으며, 정확한 RVI 지표가 아닙니다.
            # 향후 정확한 RVI 로직으로 교체해야 합니다.
            df[f'Relative_Vigor_Index_{period}'] = ta.rsi(df['close'], length=period)
        return df

    def calculate_vr(df, periods):
        # 'ta' 라이브러리에 VR(Volume Ratio)이 없으므로 직접 구현
        def volume_ratio(close, volume, period):
            vr = []
            for i in range(len(close)):
                if i < period:
                    vr.append(None)
                else:
                    vol_up = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] > close[j - 1])
                    vol_down = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] < close[j - 1])
                    vol_same = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] == close[j - 1])

                    # 분모가 0이 되는 경우 (하락 거래량 + 보합 거래량/2 가 0일 때) 처리
                    # 이는 해당 기간 동안 하락 또는 보합이 없었음을 의미하므로, 매수 압력이 매우 강한 것으로 간주합니다.
                    # 일반적으로 VR 값은 100을 기준으로 해석하므로, 이 경우 100을 반환하거나 매우 큰 값을 설정할 수 있습니다. 여기서는 100으로 설정.
                    denominator = vol_down + vol_same / 2
                    if denominator == 0:
                        vr_value = 100  # 또는 매우 큰 값(예: 1000)으로 설정하여 강한 매수 신호 표현
                    else:
                        vr_value = (vol_up + vol_same / 2) / denominator * 100
                    vr.append(vr_value)
            return vr
        for period in periods:
            df[f'VR_{period}'] = volume_ratio(df['close'], df['volume'], period=period)
        return df

    def calculate_cci(df, periods):
        for period in periods:
            df[f'CCI_{period}'] = ta.cci(df['high'], df['low'], df['close'], length=period)
        return df

    def calculate_disparity_index(df, periods):
        for period in periods:
            df[f'disparity_index_{period}'] = (df['close'] / df['close'].rolling(window=period).mean()) * 100
        return df

    def calculate_moving_averages(df, periods):
        for period in periods:
            df[f'price_ma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'volume_ma_{period}'] = df['volume'].rolling(window=period).mean()
        return df

    # 메모리 효율성을 위해 데이터 타입 다운캐스팅
    data['close'] = pd.to_numeric(data['close'], downcast='float')
    data['high'] = pd.to_numeric(data['high'], downcast='float')
    data['low'] = pd.to_numeric(data['low'], downcast='float')
    data['volume'] = pd.to_numeric(data['volume'], downcast='float')

    # 전역 변수에서 설정된 파라미터들을 가져옴
    global atr_periods, stoch_periods, bollinger_periods, ichimoku_periods, supertrend_settings
    global parabolic_sar_settings, williams_r_periods, momentum_periods, roc_periods, cmo_periods
    global mfi_periods, rsi_periods, efi_periods, rvi_periods, vr_periods, cci_periods
    global disparity_periods, moving_average_periods

    # 모든 지표 계산 함수를 순차적으로 호출
    # 향후에는 'feature_match' 함수를 통해 사용자가 선택한 지표만 계산하도록 개선 가능
    data = calculate_atr(data, atr_periods)
    data = calculate_vwap(data)
    data = calculate_stoch(data, stoch_periods)
    data = calculate_obv(data)
    data = calculate_bollinger_bands(data, bollinger_periods)
    data = calculate_ichimoku(data, ichimoku_periods)
    data = calculate_supertrend(data, supertrend_settings)
    data = calculate_parabolic_sar(data, parabolic_sar_settings)
    data = calculate_williams_r(data, williams_r_periods)
    data = calculate_momentum(data, momentum_periods)
    data = calculate_roc(data, roc_periods)
    data = calculate_cmo(data, cmo_periods)
    data = calculate_mfi(data, mfi_periods)
    data = calculate_rsi(data, rsi_periods)
    data = calculate_ad_line(data)
    data = calculate_efi(data, efi_periods)
    data = calculate_rvi(data, rvi_periods)
    data = calculate_vr(data, vr_periods)
    data = calculate_cci(data, cci_periods)
    data = calculate_disparity_index(data, disparity_periods)
    data = calculate_moving_averages(data, moving_average_periods)

    return data