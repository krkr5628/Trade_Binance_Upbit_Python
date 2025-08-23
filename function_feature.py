# -*- coding: utf-8 -*-
"""
[File: function_feature.py]
[Author: Jules (AI Agent)]
[Date: 2025-08-23]

[Summary]
This module generates technical analysis features for use in machine learning models.
Based on the `ta` library, it includes functions to calculate various indicators
from time-series data.

[Global Variables]
- `atr_periods`, `stoch_periods`, etc.: Lists containing the periods and settings
  for each technical indicator calculation. They are initialized by the `feature_inital_match` function.

[Dependencies & Interconnections]

[Incoming Calls (External modules calling this module)]
- `Main.py` -> `feature_inital_match()`: Initializes indicator calculation parameters at program startup.
- `Main.py` -> `get_prediction()`: Requests a dummy prediction result every minute.
- `function_complex.py` -> `data_feature_1()`: Requests technical indicator calculation whenever candle data is updated.

[Outgoing Calls (This module calling external modules)]
- None. (Only calls external libraries like `ta`, `pandas`, etc.)

[Global Variable Access]
- `data_feature_1()` -> `atr_periods`, `stoch_periods`, etc. (READ): Reads the global lists declared in this module
  to calculate all technical indicators according to the specified settings.

[Note]
- The `calculate_rvi` function currently uses RSI as a substitute for the actual RVI, so caution is advised.
- The `get_prediction` function is currently a dummy function that returns a random prediction, not a real model's output.
"""

# Import 'ta' (Technical Analysis) library and pandas
import ta
import pandas as pd

# Import 'function' module (not directly used in the current code)
import function

# List to store user-selected indicator settings (currently unused)
feature_simple = []

# Global lists to store calculation periods for each technical indicator
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

# Function to set the default parameters for technical indicator calculations
def feature_inital_match():
    """
    Initializes the global lists with default periods and settings for each technical indicator calculation.
    This function should be called once at program startup.
    """
    global atr_periods, stoch_periods, bollinger_periods, ichimoku_periods, supertrend_settings
    global parabolic_sar_settings, williams_r_periods, momentum_periods, roc_periods, cmo_periods
    global mfi_periods, rsi_periods, efi_periods, rvi_periods, vr_periods, cci_periods
    global disparity_periods, moving_average_periods

    # Set various periods for each indicator to generate multiple versions
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

# Function to filter parameters for user-selected indicators (currently not implemented)
def feature_match():
    """
    Filters the parameters for technical indicators to be calculated,
    based on `function.feature_data` (loaded from a settings file). (Currently not implemented).
    """
    global feature_simple, atr_periods, stoch_periods # ... and all other global variables

    # Iterate through the feature_data DataFrame and get settings for applied indicators
    for _, feature in function.feature_data.iterrows():
        # This part requires actual implementation.
        pass

# Main function to calculate and add all technical indicators to a DataFrame
def data_feature_1(data):
    """
    Calculates all defined technical indicators for the input OHLCV DataFrame and adds them as columns.
    - data: A pandas DataFrame containing 'open', 'high', 'low', 'close', 'volume' columns.
    - Returns: The DataFrame with added technical indicators.
    """

    # --- Internal helper functions for calculating each technical indicator ---

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
        # Implemented manually as Supertrend is not in the 'ta' library.
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
            # WARNING: The 'ta' library does not have a built-in RVI (Relative Vigor Index).
            # The code below uses RSI as a temporary substitute and is NOT an accurate RVI indicator.
            # This should be replaced with a correct RVI logic in the future.
            df[f'Relative_Vigor_Index_{period}'] = ta.rsi(df['close'], length=period)
        return df

    def calculate_vr(df, periods):
        # Implemented manually as VR (Volume Ratio) is not in the 'ta' library.
        def volume_ratio(close, volume, period):
            vr = []
            for i in range(len(close)):
                if i < period:
                    vr.append(None)
                else:
                    vol_up = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] > close[j - 1])
                    vol_down = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] < close[j - 1])
                    vol_same = sum(volume[j] for j in range(i - period + 1, i + 1) if close[j] == close[j - 1])

                    # Handle division by zero (when down-volume + half of same-volume is zero).
                    # This implies no downward or neutral pressure, indicating strong buying pressure.
                    # VR is typically interpreted around the 100 level, so returning 100 or a very large number is appropriate. Here, 100 is used.
                    denominator = vol_down + vol_same / 2
                    if denominator == 0:
                        vr_value = 100  # Or a very large value (e.g., 1000) to signify strong buy signal
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

    # Downcast data types for memory efficiency
    data['close'] = pd.to_numeric(data['close'], downcast='float')
    data['high'] = pd.to_numeric(data['high'], downcast='float')
    data['low'] = pd.to_numeric(data['low'], downcast='float')
    data['volume'] = pd.to_numeric(data['volume'], downcast='float')

    # Get parameters from global variables
    global atr_periods, stoch_periods, bollinger_periods, ichimoku_periods, supertrend_settings
    global parabolic_sar_settings, williams_r_periods, momentum_periods, roc_periods, cmo_periods
    global mfi_periods, rsi_periods, efi_periods, rvi_periods, vr_periods, cci_periods
    global disparity_periods, moving_average_periods

    # Sequentially call all indicator calculation functions
    # In the future, this could be improved to only calculate indicators selected via feature_match()
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

# Dummy prediction function
def get_prediction(data):
    """
    Returns a dummy prediction based on the given feature data.
    Currently returns a random choice of 'Buy', 'Sell', or 'Hold' instead of using a real model.
    - data: Feature data to be used for prediction (currently unused).
    - Returns: A prediction string.
    """
    import random
    # When a real model is implemented, this part will be replaced with code like model.predict(data)
    predictions = ["Buy", "Sell", "Hold"]
    return random.choice(predictions)