import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
import statsmodels.api as sm
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

# Binance API keys
api_key = 'TAAgJilKcF9LHg977hGa3fVXdd9TUv6EmaZu7YgkCa4f8aAcxT5lvRI1gkh8mvw2'
api_secret = 'Yw48JHkJu3dz0YpJrPJz9ektNHUvYZtNePTeQLzDAe0CRk33wyKbebyRV0q4xwJk'

# Binance API alternatif URL'leri
ALTERNATIVE_URLS = [
    'https://api.binance.com',
    'https://api2.binance.com',
    'https://api3.binance.com'
]

def get_binance_data(symbol, interval, start_str, end_str):
    for url in ALTERNATIVE_URLS:
        try:
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'urls': {
                    'api': url
                }
            })
            klines = exchange.fetch_ohlcv(symbol, interval, since=exchange.parse8601(start_str), limit=1000)
            if not klines or len(klines) < 51:
                continue
            
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df = df.astype(float)
            return df
        except ccxt.NetworkError as e:
            st.warning(f"Network hatası ({url}): {e}")
        except ccxt.ExchangeError as e:
            st.warning(f"Exchange hatası ({url}): {e}")
        except Exception as e:
            st.error(f"Genel hata ({url}): {e}")

    st.error("Tüm alternatif API uç noktaları başarısız oldu.")
    return pd.DataFrame()

def get_all_usdt_pairs():
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
        })
        exchange.load_markets()
        symbols = exchange.markets.keys()
        usdt_pairs = [s for s in symbols if s.endswith('/USDT')]
        return usdt_pairs
    except ccxt.NetworkError as e:
        st.warning(f"Network hatası: {e}")
    except ccxt.ExchangeError as e:
        st.warning(f"Exchange hatası: {e}")
    except Exception as e:
        st.error(f"Genel hata: {e}")
    return []

def calculate_indicators(df):
    # Göstergeler hesaplama kodu burada...
    return df

def generate_signals(df):
    # Sinyaller oluşturma kodu burada...
    return df

def forecast_next_price(df):
    # Gelecek fiyat tahmini kodu burada...
    return np.nan

def calculate_expected_price(df):
    # Beklenen fiyat hesaplama kodu burada...
    return np.nan, np.nan

def calculate_trade_levels(df, entry_pct=0.02, take_profit_pct=0.05, stop_loss_pct=0.02):
    # Ticaret seviyelerini hesaplama kodu burada...
    return np.nan, np.nan, np.nan

def plot_to_png(df, symbol):
    # Grafik çizim kodu burada...
    return ""

def process_symbol(symbol, interval, start_str, end_str):
    df = get_binance_data(symbol, interval, start_str, end_str)
    if df.empty:
        return None

    try:
        df = calculate_indicators(df)
        df = generate_signals(df)
        forecast = forecast_next_price(df)
        expected_price, expected_increase_percentage = calculate_expected_price(df)
        entry_price, take_profit_price, stop_loss_price = calculate_trade_levels(df)
        
        if df['Buy_Signal'].iloc[-1] and expected_increase_percentage >= 5:
            return {
                'coin_name': symbol,
                'price': df['close'].iloc[-1],
                'expected_price': expected_price,
                'expected_increase_percentage': expected_increase_percentage,
                'sma_50': df['SMA_50'].iloc[-1],
                'rsi_14': df['RSI'].iloc[-1],
                'macd_line': df['MACD_Line'].iloc[-1],
                'macd_signal': df['MACD_Signal'].iloc[-1],
                'bb_upper': df['BB_Upper'].iloc[-1],
                'bb_middle': df['BB_Middle'].iloc[-1],
                'bb_lower': df['BB_Lower'].iloc[-1],
                'atr': df['ATR'].iloc[-1],
                'stoch_k': df['%K'].iloc[-1],
                'stoch_d': df['%D'].iloc[-1],
                'forecast_next_day_price': forecast,
                'entry_price': entry_price,
                'take_profit_price': take_profit_price,
                'stop_loss_price': stop_loss_price,
                'plot': plot_to_png(df, symbol)
            }
    except Exception as e:
        st.error(f"İşleme hatası ({symbol}): {e}")
        return None

def main():
    st.title('Kripto Para Analizi')
    
    interval = st.selectbox('Zaman Aralığı', ['1d', '1h', '30m', '15m', '5m', '1m'], index=0)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=51)
    start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    if st.button('Analiz Başlat'):
        usdt_pairs = get_all_usdt_pairs()
        if not usdt_pairs:
            st.error("USDT paritesi bulunamadı.")
            return
        
        with ThreadPoolExecutor() as executor:
            future_to_symbol = {executor.submit(process_symbol, symbol, interval, start_str, end_str): symbol for symbol in usdt_pairs}
            results = []
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        for result in results:
            st.subheader(f"{result['coin_name']} Analizi")
            st.write(f"Mevcut Fiyat: ${result['price']:.2f}")
            st.write(f"Beklenen Fiyat: ${result['expected_price']:.2f}")
            st.write(f"Beklenen Artış Yüzdesi: {result['expected_increase_percentage']:.2f}%")
            st.write(f"SMA 50: ${result['sma_50']:.2f}")
            st.write(f"RSI 14: {result['rsi_14']:.2f}")
            st.write(f"MACD Line: {result['macd_line']:.2f}")
            st.write(f"MACD Signal: {result['macd_signal']:.2f}")
            st.write(f"BB Üst Bandı: ${result['bb_upper']:.2f}")
            st.write(f"BB Orta Bandı: ${result['bb_middle']:.2f}")
            st.write(f"BB Alt Bandı: ${result['bb_lower']:.2f}")
            st.write(f"ATR: {result['atr']:.2f}")
            st.write(f"Stochastic %K: {result['stoch_k']:.2f}")
            st.write(f"Stochastic %D: {result['stoch_d']:.2f}")
            st.write(f"Öngörülen Ertesi Gün Fiyatı: ${result['forecast_next_day_price']:.2f}")
            st.write(f"Giriş Fiyatı: ${result['entry_price']:.2f}")
            st.write(f"Kar Alma Fiyatı: ${result['take_profit_price']:.2f}")
            st.write(f"Zarar Durdur Fiyatı: ${result['stop_loss_price']:.2f}")
            st.image(f"data:image/png;base64,{result['plot']}", use_column_width=True)

if __name__ == '__main__':
    main()
