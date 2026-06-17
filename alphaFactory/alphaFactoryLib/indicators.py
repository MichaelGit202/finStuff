#Good

# simple moving average
def SMA(data_window, lag_window=20, col="Close"):
    if len(data_window) < lag_window:
        return None
    window = [bar[col] for bar in data_window]
    return sum(window[-lag_window:]) / lag_window



# ADX is a momentum oscillator which can offer insights into whether an asset is trending and if so how significantly. 
# It quantifies price action, allowing traders to see whether a particular move falls within a trending or non-trending market
# aiding entry or exit decisions. 
# from: https://tabtrader.com/academy/articles/average-directional-index-adx-explained

# I love side effects
ADX_prior_smoothed_plus_dm = 0.0
ADX_prior_smoothed_minus_dm = 0.0
ADX_prior_ATR = 0.0
ADX_prior_ADX = 0.0
ADX_dx_history = [] 
# yea holy fuck i tried, but i just had gemini make it
"Avg Directional Index, Trend strength"
# Returns a value between 0 and 100, with higher values indicating a stronger trend. Either skyrocketing or plummeting. 
# 20 to 25: A trend is starting to break out or form.
# 25 to 50: A strong, established trend is underway.
# Over 50: An extremely strong, historic trend (often unsustainable over the long term).
def ADX(data_window, window=14):
    global ADX_prior_smoothed_plus_dm, ADX_prior_smoothed_minus_dm
    global ADX_prior_ATR, ADX_prior_ADX, ADX_dx_history

    if len(data_window) < 2:
        return None
    
    prev_bar = data_window[-2]
    last_bar = data_window[-1]

    # 1. Calculate Raw Directional Movement
    up_move = last_bar["High"] - prev_bar["High"]
    down_move = prev_bar["Low"] - last_bar["Low"]

    current_plus_dm = 0
    current_minus_dm = 0

    if up_move > down_move and up_move > 0:
        current_plus_dm = up_move
    elif down_move > up_move and down_move > 0:
        current_minus_dm = down_move

    # 2. Wilder's Smoothing for both DM tracks independently
    smoothed_plus_dm_today = ADX_prior_smoothed_plus_dm - (ADX_prior_smoothed_plus_dm / window) + current_plus_dm
    smoothed_minus_dm_today = ADX_prior_smoothed_minus_dm - (ADX_prior_smoothed_minus_dm / window) + current_minus_dm

    # 3. Calculate True Range and Smoothed ATR
    # Note: Using your key case lowercase 'close' from your original snippet
    true_range = max(
        last_bar["High"] - last_bar["Low"], 
        abs(last_bar["High"] - prev_bar["Close"]), 
        abs(last_bar["Low"] - prev_bar["Close"])
    )
    
    ATR_today = ADX_prior_ATR - (ADX_prior_ATR / window) + true_range

    # Guard against division by zero if ATR is completely flat
    if ATR_today == 0:
        return 0

    # 4. Calculate Directional Indicators (Fixed algebraic syntax matching your image)
    pos_DI = (smoothed_plus_dm_today / ATR_today) * 100
    neg_DI = (smoothed_minus_dm_today / ATR_today) * 100

    # 5. Calculate DX (Added absolute value to match image)
    dx_denom = pos_DI + neg_DI
    DX = (abs(pos_DI - neg_DI) / dx_denom * 100) if dx_denom != 0 else 0

    # 6. Smooth DX to get final ADX
    ADX_dx_history.append(DX)
    
    if len(ADX_dx_history) < window:
        # We don't have enough days yet to calculate an ADX baseline
        current_adx = 0 
    elif len(ADX_dx_history) == window:
        # First ADX point is a Simple Moving Average of the first 14 DX values
        current_adx = sum(ADX_dx_history) / window
    else:
        # Standard day-to-day rolling ADX formula
        current_adx = (ADX_prior_ADX * (window - 1) + DX) / window

    # 7. Update your global state variables for tomorrow's run
    ADX_prior_smoothed_plus_dm = smoothed_plus_dm_today
    ADX_prior_smoothed_minus_dm = smoothed_minus_dm_today
    ADX_prior_ATR = ATR_today
    ADX_prior_ADX = current_adx

    return current_adx







# RSI measures the speed and magnitude of a security's recent price changes
"relative strength index, The velocity of the price change and the magnitude of the price change"
# returns 0 to 100, with high values indicating overbought conditions and low values indicating oversold conditions
# 0 to 30: Oversold conditions, potential buying opportunity.
# 30 to 70: Neutral zone, no clear overbought or oversold conditions.
# 70 to 100: Overbought conditions, potential selling opportunity.
def RSI(data_window, window=14, col="Close"):
    if len(data_window) < 2:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, min(len(data_window), window + 1)):
        change = data_window[-i][col] - data_window[-i - 1][col]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-change)

    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window

    if avg_loss == 0:
        return 100  # Prevent division by zero; implies very strong upward momentum

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


# measures the closing price of a security relative to its high-low range over a specific period
"stochastic oscillator, The position of the current close relative to the recent trading range"
# returns 0 to 100, with high values indicating overbought conditions and low values indicating oversold conditions
# Under 20: The asset is oversold, closing near the bottom of its recent range.
# 20 to 80: The asset is trading within its normal historical range.
# Over 80: The asset is overbought, closing near the top of its recent range.
def stochastic_oscillator(data_window, window=14, col="Close"):
    if len(data_window) < window:
        return None
    
    recent_window = list(data_window)[-window:]
    highest_high = max(bar["High"] for bar in recent_window)
    lowest_low = min(bar["Low"] for bar in recent_window)
    
    if highest_high == lowest_low:
        return 50  # Prevent division by zero; implies no price movement

    last_close = data_window[-1][col]
    k_percent = ((last_close - lowest_low) / (highest_high - lowest_low)) * 100
    
    return k_percent


# the point in which i gave up lol


# -------------------------------------------------------
# ATR - Average True Range
# -------------------------------------------------------
ATR_prior = 0.0

"Average True Range, Absolute volatility — how much is price actually moving?"
# Returns the average size of price moves over the window period, in price units.
# Small ATR: Low volatility, price is consolidating.
# Large ATR: High volatility, price is making big moves.
def ATR(data_window, window=14):
    global ATR_prior

    if len(data_window) < 2:
        return None

    prev_bar = data_window[-2]
    last_bar = data_window[-1]

    true_range = max(
        last_bar["High"] - last_bar["Low"],
        abs(last_bar["High"] - prev_bar["Close"]),
        abs(last_bar["Low"] - prev_bar["Close"])
    )

    # Wilder's smoothing (same method as ADX)
    if ATR_prior == 0.0:
        ATR_prior = true_range
        return ATR_prior

    ATR_today = ATR_prior - (ATR_prior / window) + true_range
    ATR_prior = ATR_today
    return ATR_today


# -------------------------------------------------------
# Bollinger Band Width
# -------------------------------------------------------
"Bollinger Band Width, Relative volatility — is the market squeezing or expanding?"
# Returns (upper - lower) / middle, i.e. band width as a fraction of price.
# Falling width (squeeze): Volatility is contracting, often precedes a big move.
# Rising width: Volatility is expanding, trend is accelerating.
def bollinger_band_width(data_window, window=20, num_std=2, col="Close"):
    if len(data_window) < window:
        return None

    closes = [bar[col] for bar in list(data_window)[-window:]]
    mean = sum(closes) / window
    variance = sum((c - mean) ** 2 for c in closes) / window
    std = variance ** 0.5

    upper = mean + num_std * std
    lower = mean - num_std * std

    if mean == 0:
        return None

    return (upper - lower) / mean


# -------------------------------------------------------
# OBV - On-Balance Volume
# -------------------------------------------------------
OBV_prior_value = 0.0
OBV_prior_close = None

"On-Balance Volume, Cumulative volume flow — are buyers or sellers in control?"
# Returns a running cumulative total (no fixed range).
# Rising OBV with rising price: Strong uptrend confirmed by volume.
# Falling OBV with rising price: Divergence — move may not be sustainable.
def OBV(data_window):
    global OBV_prior_value, OBV_prior_close

    if len(data_window) < 1:
        return None

    last_bar = data_window[-1]
    current_close = last_bar["Close"]
    current_volume = last_bar["Volume"]

    if OBV_prior_close is None:
        OBV_prior_close = current_close
        return OBV_prior_value

    if current_close > OBV_prior_close:
        OBV_prior_value += current_volume
    elif current_close < OBV_prior_close:
        OBV_prior_value -= current_volume
    # equal close: OBV unchanged

    OBV_prior_close = current_close
    return OBV_prior_value


# -------------------------------------------------------
# CMF - Chaikin Money Flow
# -------------------------------------------------------
"Chaikin Money Flow, Accumulation vs. distribution — who is winning over the window?"
# Returns a value between -1 and +1.
# Above 0: Accumulation (buying pressure dominant).
# Below 0: Distribution (selling pressure dominant).
# Above +0.25 or below -0.25: Strong signal.
def CMF(data_window, window=20):
    if len(data_window) < window:
        return None

    recent = list(data_window)[-window:]

    total_mfv = 0.0
    total_volume = 0.0

    for bar in recent:
        high = bar["High"]
        low = bar["Low"]
        close = bar["Close"]
        volume = bar["Volume"]

        price_range = high - low
        if price_range == 0:
            mfm = 0.0
        else:
            mfm = ((close - low) - (high - close)) / price_range

        total_mfv += mfm * volume
        total_volume += volume

    if total_volume == 0:
        return 0.0

    return total_mfv / total_volume


# -------------------------------------------------------
# Z-Score of Price
# -------------------------------------------------------
"Z-Score of Price, Mean reversion — how stretched is price from its average?"
# Returns standard deviations from the mean. No fixed range but typically -3 to +3.
# Above +2: Price is historically high relative to recent average, may revert down.
# Below -2: Price is historically low relative to recent average, may revert up.
# Near 0: Price is close to its recent mean.
def z_score(data_window, window=20, col="Close"):
    if len(data_window) < window:
        return None

    closes = [bar[col] for bar in list(data_window)[-window:]]
    mean = sum(closes) / window
    variance = sum((c - mean) ** 2 for c in closes) / window
    std = variance ** 0.5

    if std == 0:
        return 0.0

    return (closes[-1] - mean) / std


# -------------------------------------------------------
# Donchian Channel Position
# -------------------------------------------------------
"Donchian Channel Position, Range position — where is price within its recent high/low range?"
# Returns 0 to 1, where 0 = at the lowest low and 1 = at the highest high.
# Above 0.8: Price near top of range, potential breakout or overbought.
# Below 0.2: Price near bottom of range, potential breakdown or oversold.
# Near 0.5: Price in the middle of the range.
def donchian_channel_position(data_window, window=20, col="Close"):
    if len(data_window) < window:
        return None

    recent = list(data_window)[-window:]
    highest_high = max(bar["High"] for bar in recent)
    lowest_low = min(bar["Low"] for bar in recent)

    if highest_high == lowest_low:
        return 0.5  # No range movement

    current_close = data_window[-1][col]
    return (current_close - lowest_low) / (highest_high - lowest_low)

#TODO jank
# tags are there so when GP is creating new indicators it wont add exact matches
FUNCTION_ARR_DICT = {
    1 : {"function" : SMA, "name" : "SMA", "categories": ["trend"], "type": "lagging"}, 
    2 : {"function" : ADX, "name" : "ADX", "categories": ["trend"], "type": "lagging"}, 
    3 : {"function" : RSI, "name" : "RSI", "categories": ["momentum"], "type": "leading"}, 
    4 : {"function" : stochastic_oscillator, "name" : "stochastic_oscillator", "categories": ["momentum"], "type": "leading"}, 
    5 : {"function" : ATR, "name" : "ATR", "categories": ["volatility"], "type": "coincident"}, 
    6 : {"function" : bollinger_band_width, "name" : "bollinger_band_width", "categories": ["volatility"], "type": "coincident"}, 
    7 : {"function" : OBV, "name" : "OBV", "categories": ["volume"], "type": "lagging"}, 
    8 : {"function" : CMF, "name" : "CMF", "categories": ["volume"], "type": "leading"}, 
    9 : {"function" : z_score, "name" : "z_score", "categories": ["statistical"], "type": "leading"}, 
    10 : {"function" : donchian_channel_position, "name" : "donchian_channel_position", "categories": ["trend"], "type": "coincident"}
}

function_categories = {
    SMA: {"categories": ["trend"], "type": "lagging"},
    ADX: {"categories": ["trend"], "type": "lagging"},  
    RSI: {"categories": ["momentum"], "type": "leading"},
    stochastic_oscillator: {"categories": ["momentum"], "type": "leading"},
    ATR: {"categories": ["volatility"], "type": "coincident"},
    bollinger_band_width: {"categories": ["volatility"], "type": "coincident"},
    OBV: {"categories": ["volume"], "type": "lagging"},
    CMF: {"categories": ["volume"], "type": "leading"},
    z_score: {"categories": ["statistical"], "type": "leading"},
    donchian_channel_position: {"categories": ["trend"], "type": "coincident"}  
}


def reset_indicator_state():
    global ADX_prior_smoothed_plus_dm, ADX_prior_smoothed_minus_dm
    global ADX_prior_ATR, ADX_prior_ADX, ADX_dx_history
    global ATR_prior, OBV_prior_value, OBV_prior_close

    ADX_prior_smoothed_plus_dm = 0.0
    ADX_prior_smoothed_minus_dm = 0.0
    ADX_prior_ATR = 0.0
    ADX_prior_ADX = 0.0
    ADX_dx_history = []

    ATR_prior = 0.0

    OBV_prior_value = 0.0
    OBV_prior_close = None
