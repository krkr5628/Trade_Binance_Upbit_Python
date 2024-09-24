import ta
import pandas as pd

import function

feature_simple = []

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

def feature_inital_match() :

    global atr_periods
    global stoch_periods
    global bollinger_periods
    global ichimoku_periods
    global supertrend_settings
    global parabolic_sar_settings
    global williams_r_periods
    global momentum_periods
    global roc_periods
    global cmo_periods
    global mfi_periods
    global rsi_periods
    global efi_periods
    global rvi_periods
    global vr_periods
    global cci_periods
    global disparity_periods
    global moving_average_periods

    # 모든 계산 수행(initial)
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

def feature_match() :

    global atr_periods
    global stoch_periods
    global bollinger_periods
    global ichimoku_periods
    global supertrend_settings
    global parabolic_sar_settings
    global williams_r_periods
    global momentum_periods
    global roc_periods
    global cmo_periods
    global mfi_periods
    global rsi_periods
    global efi_periods
    global rvi_periods
    global vr_periods
    global cci_periods
    global disparity_periods
    global moving_average_periods

    for feature in function.feature_data.iterrows() :

        # type 제외하고 값 입력
        # type,index1,index2,index3,index4,index5,apply1,apply2,apply3,apply4,apply5
        feature_time_tmp = []

        for idx in range(5) :
            if (feature[idx + 1]):
                feature_time_tmp.append(feature[idx + 6])

        feature_simple.append(feature_time_tmp)

#지속적 업데이를 위한 구조화 필수
def data_feature_1(data) :
    # ATR 계산 함수
    def calculate_atr(df, periods):
        for period in periods:
            df[f'atr_{period}'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=period)
        return df

    # VWAP 계산 함수
    def calculate_vwap(df):
        df['vwap'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'])
        return df

    # Stochastic Oscillator 계산 함수
    def calculate_stoch(df, periods):
        for period, smooth in periods:
            df[f'stoch_%k_{period}_{smooth}'] = ta.momentum.stoch(df['high'], df['low'], df['close'], window=period,
                                                                  smooth_window=smooth)
            df[f'stoch_%d_{period}_{smooth}'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'],
                                                                         window=period, smooth_window=smooth)
        return df

    # OBV 계산 함수
    def calculate_obv(df):
        df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        return df

    # Bollinger Bands 계산 함수
    def calculate_bollinger_bands(df, periods):
        for period in periods:
            bollinger = ta.volatility.BollingerBands(df['close'], window=period)
            df[f'bollinger_hband_{period}'] = bollinger.bollinger_hband()
            df[f'bollinger_lband_{period}'] = bollinger.bollinger_lband()
        return df

    # Ichimoku 계산 함수
    def calculate_ichimoku(df, periods):
        for period in periods:
            df[f'ichimoku_base_{period}'] = ta.trend.ichimoku_base_line(df['high'], df['low'], window1=period)
            df[f'ichimoku_conversion_{period}'] = ta.trend.ichimoku_conversion_line(df['high'], df['low'],
                                                                                    window1=period)
        return df

    # Supertrend 계산 함수
    def calculate_supertrend(df, settings):
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

                    if df['in_uptrend'].iloc[current] and df['lowerband'].iloc[current] < df['lowerband'].iloc[
                        previous]:
                        df.loc[df.index[current], 'lowerband'] = df['lowerband'].iloc[previous]

                    if not df['in_uptrend'].iloc[current] and df['upperband'].iloc[current] > df['upperband'].iloc[
                        previous]:
                        df.loc[df.index[current], 'upperband'] = df['upperband'].iloc[previous]

            df[f'supertrend_upper_{period}_{multiplier}_{atr_period}'] = df['upperband']
            df[f'supertrend_lower_{period}_{multiplier}_{atr_period}'] = df['lowerband']
            df[f'supertrend_in_uptrend_{period}_{multiplier}_{atr_period}'] = df['in_uptrend']

        return df

    #Parabolic SAR
    def calculate_parabolic_sar(df, settings):
        for af, max_af in settings:
            key = f'Parabolic_SAR_{af}'
            df[key] = ta.psar(df['high'], df['low'], df['close'], af=af, max_af=max_af)[f'PSARl_{af}_{max_af}']
        return df

    #Williams %R
    def calculate_williams_r(df, periods):
        for period in periods:
            key = f'Williams_%R_{period}'
            df[key] = ta.willr(df['high'], df['low'], df['close'], length=period)
        return df

    #Momentum
    def calculate_momentum(df, periods):
        for period in periods:
            key = f'Momentum_{period}'
            df[key] = ta.mom(df['close'], length=period)
        return df

    #Rate of Change (ROC)
    def calculate_roc(df, periods):
        for period in periods:
            key = f'ROC_{period}'
            df[key] = ta.roc(df['close'], length=period)
        return df

    #Chande Momentum Oscillator (CMO)
    def calculate_cmo(df, periods):
        for period in periods:
            key = f'CMO_{period}'
            df[key] = ta.cmo(df['close'], length=period)
        return df

    #Money Flow Index (MFI)
    def calculate_mfi(df, periods):
        for period in periods:
            key = f'MFI_{period}'
            df[key] = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=period)
        return df

    #Relative Strength Index (RSI)
    def calculate_rsi(df, periods):
        for period in periods:
            key = f'RSI_{period}'
            df[key] = ta.rsi(df['close'], length=period)
        return df

    #Accumulation/Distribution Line (A/D Line)
    def calculate_ad_line(df):
        df['Accumulation_Distribution_Line'] = ta.ad(df['high'], df['low'], df['close'], df['volume'])
        return df

    #Elder's Force Index (EFI)
    def calculate_efi(df, periods):
        for period in periods:
            key = f'Elder_Force_Index_{period}'
            df[key] = ta.efi(df['close'], df['volume'], length=period)
        return df

    #Relative Vigor Index (RVI)
    def calculate_rvi(df, periods):
        for period in periods:
            key = f'Relative_Vigor_Index_{period}'
            df[key] = ta.rsi(df['close'], length=period)  # 대체
        return df

    #Volume Ratio (VR)
    def calculate_vr(df, periods):
        def volume_ratio(close, volume, period):
            vr = []
            for i in range(len(close)):
                if i < period:
                    vr.append(None)
                else:
                    vol_up = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] > close[j - 1])
                    vol_down = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] < close[j - 1])
                    vol_same = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] == close[j - 1])
                    vr_value = (vol_up + vol_same / 2) / (vol_down + vol_same / 2) * 100
                    vr.append(vr_value)
            return vr

        for period in periods:
            key = f'VR_{period}'
            df[key] = volume_ratio(df['close'], df['volume'], period=period)
        return df

    #Commodity Channel Index (CCI)
    def calculate_cci(df, periods):
        for period in periods:
            key = f'CCI_{period}'
            df[key] = ta.cci(df['high'], df['low'], df['close'], length=period)
        return df

    #이격도(Price Disparity Index)
    def calculate_disparity_index(df, periods):
        for period in periods:
            df[f'disparity_index_{period}'] = (df['close'] / df['close'].rolling(window=period).mean()) * 100
        return df

    #이동평균선(Moving Averages)
    def calculate_moving_averages(df, periods):
        for period in periods:
            df[f'price_ma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'volume_ma_{period}'] = df['volume'].rolling(window=period).mean()
        return df

    #지표 다운캐스팅(메모리 사용 감소)
    data['close'] = pd.to_numeric(data['close'], downcast='float')
    data['high'] = pd.to_numeric(data['high'], downcast='float')
    data['low'] = pd.to_numeric(data['low'], downcast='float')
    data['volume'] = pd.to_numeric(data['volume'], downcast='float')

    #
    global atr_periods
    global stoch_periods
    global bollinger_periods
    global ichimoku_periods
    global supertrend_settings
    global parabolic_sar_settings
    global williams_r_periods
    global momentum_periods
    global roc_periods
    global cmo_periods
    global mfi_periods
    global rsi_periods
    global efi_periods
    global rvi_periods
    global vr_periods
    global cci_periods
    global disparity_periods
    global moving_average_periods

    #사용하는 지표만 선택적으로 사용하도록 향후 구성
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