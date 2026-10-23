import os
import discord
from discord.ext import commands
from tradingview_ta import TA_Handler, Interval

# Cloudflare Rate Limit (Error 1015) මඟහැරීමට User-Agent Custom Header එකක් සෙට් කිරීම
import tradingview_ta
tradingview_ta.TA_Handler.SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 11aall එකදුන්වන්නේ නැතහොත් භාවිතා වන default coins
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT"]

def get_ta(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange="BINANCE",
            screener="crypto",
            interval=Interval.INTERVAL_1_HOUR
        )
        analysis = handler.get_analysis()
        indicators = analysis.indicators

        rsi = round(indicators.get("RSI", 0), 2)
        macd = round(indicators.get("MACD.macd", 0), 2)
        stoch_k = round(indicators.get("Stoch.K", 0), 2)
        stoch_d = round(indicators.get("Stoch.D", 0), 2)
        bb_upper = round(indicators.get("BB.upper", 0), 2)
        bb_lower = round(indicators.get("BB.lower", 0), 2)
        close = round(indicators.get("close", 0), 4)
        summary = analysis.summary.get("RECOMMENDATION", "N/A")

        # Buy / Sell Signal එක ලස්සනට emoji එක්ක පෙන්වීමට
        if summary == "STRONG_BUY":
            signal = "🟢 **STRONG BUY**"
        elif summary == "BUY":
            signal = "🟢 **BUY**"
        elif summary == "SELL":
            signal = "🔴 **SELL**"
        elif summary == "STRONG_SELL":
            signal = "🔴 **STRONG SELL**"
        else:
            signal = "🟡 **NEUTRAL**"

        return f"📊 **{symbol} Analysis (1H)**\n\nPrice: `${close}`\nSignal: {signal}\n\n• RSI: `{rsi}`\n• MACD: `{macd}`\n• Stoch K/D: `{stoch_k}` / `{stoch_d}`\n• BB Upper: `{bb_upper}`\n• BB Lower: `{bb_lower}`"
    except Exception as e:
        return f"❌ Error fetching data for **{symbol}**: {e}"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def ta(ctx, symbol: str = None):
    if symbol:
        symbol = symbol.upper()
        if not symbol.endswith("USDT"):
            symbol += "USDT"
        res = get_ta(symbol)
        await ctx.send(res)
    else:
        msg = "🚀 **Market Overview (1H)**\n\n"
        for sym in DEFAULT_SYMBOLS:
            res = get_ta(sym)
            msg += res + "\n-------------------\n"
        await ctx.send(msg)

bot.run(os.getenv('DISCORD_TOKEN'))
