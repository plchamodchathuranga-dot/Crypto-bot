import discord
from discord.ext import commands
from tradingview_ta import TA_Handler, Interval
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# !taall ගැහුවම එන්න ඕන ප්‍රධාන කොයින් ලැයිස්තුව
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

        # Buy / Sell Signal එක ලස්සනට Emojis එක්ක පෙන්වීම
        if summary == "STRONG_BUY":
            signal = "🟢 **STRONG BUY**"
        elif summary == "BUY":
            signal = "🟢 **BUY**"
        elif summary == "SELL":
            signal = "🔴 **SELL**"
        elif summary == "STRONG_SELL":
            signal = "🔴 **STRONG SELL**"
        else:
            signal = "⚪ **NEUTRAL**"

        return f"📌 **{symbol}** (Price: `${close}`)\n" \
               f"• Signal: {signal}\n" \
               f"• RSI (14): `{rsi}`\n" \
               f"• MACD: `{macd}`\n" \
               f"• Stoch RSI: K=`{stoch_k}`, D=`{stoch_d}`\n" \
               f"• Bollinger Bands: Upper=`{bb_upper}`, Lower=`{bb_lower}`\n"
    except Exception as e:
        return f"❌ **{symbol}** සඳහා දත්ත සොයාගැනීමට නොහැකි විය. Coin Symbol එක නිවැරදිදැයි බලන්න."

@bot.event
async def on_ready():
    print(f"Bot සූදානම්! Logged in as {bot.user}")

# ලෝකයේ ඕනෑම Coin එකක් බලන්න (!ta pepe, !ta sui, !ta btc ආදී ලෙස)
@bot.command()
async def ta(ctx, coin: str):
    symbol = coin.upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    
    await ctx.send(f"⏳ **{symbol}** දත්ත ලබාගනිමින් පවතී...")
    result = get_ta(symbol)
    await ctx.send(result)

# ප්‍රධාන Coins එකවර බලන්න (!taall)
@bot.command()
async def taall(ctx):
    await ctx.send("⏳ සියලුම කොයින්වල දත්ත ලබාගනිමින් පවතී...")
    response = "📊 **Crypto TA Summary (1H Interval)**\n\n"
    for sym in DEFAULT_SYMBOLS:
        response += get_ta(sym) + "\n"
    await ctx.send(response)

# ඔබේ Discord Bot Token එක මෙතැනට දාන්න
bot.run(os.getenv('DISCORD_TOKEN'))
