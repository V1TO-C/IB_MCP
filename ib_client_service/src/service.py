import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from ib_async import IB, util, Contract, Stock, Bond, MarketOrder
from dotenv import load_dotenv
import os
import pandas as pd # Added pandas for DataFrame handling

# Configure logging
util.logToConsole(logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Global IB instance
ib = IB()

# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to IB TWS/Gateway
    logger.info("Attempting to connect to IB Gateway/TWS...")
    try:
        host = os.getenv("IB_HOST", "127.0.0.1")
        port = int(os.getenv("IB_PORT", 7497)) # 7497 for TWS paper, 7496 for TWS live, 4002 for Gateway paper, 4001 for Gateway live
        clientId = int(os.getenv("IB_CLIENT_ID", 1))
        
        await ib.connectAsync(host, port, clientId=clientId, timeout=10) # Use connectAsync
        logger.info(f"Successfully connected to IB on {host}:{port} with clientId {clientId}")
        # Keep the event loop running in the background
        # asyncio.create_task(ib.runAsync()) # ib_async manages its own loop with connectAsync

    except asyncio.TimeoutError:
        logger.error(f"Connection to IB timed out ({host}:{port}). Ensure TWS/Gateway is running and API connections are enabled.")
        # Allow app to start but indicate connection failure? Or raise exception?
        # For now, log error and continue. Health check will fail.
    except ConnectionRefusedError:
         logger.error(f"Connection refused by IB ({host}:{port}). Check TWS/Gateway API settings.")
    except Exception as e:
        logger.error(f"Failed to connect to IB: {e}", exc_info=True)
        # Decide how to handle startup failure - maybe raise to prevent app start?

    yield # Application runs here

    # Shutdown: Disconnect from IB
    logger.info("Disconnecting from IB...")
    if ib.isConnected():
        ib.disconnect()
    logger.info("IB disconnected.")

# --- FastAPI App ---
app = FastAPI(title="IB Client Service", lifespan=lifespan)

# --- API Endpoints ---
@app.get("/health")
async def health_check():
    """Check connection status to IB TWS/Gateway."""
    if ib.isConnected():
        return {"status": "ok", "message": "Connected to IB"}
    else:
        raise HTTPException(status_code=503, detail="Service Unavailable: Not connected to IB")

# Example endpoint (to be expanded later)
@app.get("/account/summary")
async def get_account_summary():
    if not ib.isConnected():
        raise HTTPException(status_code=503, detail="Not connected to IB")
    try:
        # Example: Fetch account summary (replace 'all' with specific tags if needed)
        # Note: This requires market data subscriptions for some values.
        summary = await ib.accountSummaryAsync()
        return {"status": "ok", "summary": util.df(summary).to_dict(orient='records')} # Convert DataFrame to dict
    except Exception as e:
        logger.error(f"Error fetching account summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# --- Helper Function for Contract Creation ---
def create_contract(secType: str, conId: int = None, symbol: str = None, exchange: str = None, currency: str = "USD", **kwargs):
    """Creates an IB Contract object."""
    if conId:
        # Prioritize conId if provided
        contract = Contract(secType=secType, conId=conId, exchange=exchange, currency=currency, **kwargs)
    elif symbol and exchange:
        contract = Contract(secType=secType, symbol=symbol, exchange=exchange, currency=currency, **kwargs)
    else:
        raise ValueError("Either conId or (symbol and exchange) must be provided")
    return contract

# --- Data Endpoints ---

@app.get("/data/ticks/{secType}")
async def get_tick_data(
    secType: str,
    conId: int = Query(None, description="Contract ID (recommended)"),
    symbol: str = Query(None, description="Symbol (if conId not provided)"),
    exchange: str = Query(None, description="Exchange (if conId not provided)"),
    currency: str = Query("USD", description="Currency"),
    marketDataType: int = Query(3, description="Market data type (1=REALTIME, 2=FROZEN, 3=DELAYED, 4=DELAYED_FROZEN)")
):
    """Get snapshot market data (ticks) for a given contract."""

    if not ib.isConnected():
        raise HTTPException(status_code=503, detail="Not connected to IB")

    try:
        contract = create_contract(secType=secType.upper(), conId=conId, symbol=symbol, exchange=exchange, currency=currency)
        logger.info(f"Requesting tick data for: {contract}")

        # Qualify the contract first
        qualified_contracts = await ib.qualifyContractsAsync(contract)
        if not qualified_contracts:
            raise HTTPException(status_code=404, detail=f"Contract not found or ambiguous: {contract}")
        qualified_contract = qualified_contracts[0]
        logger.info(f"Qualified contract: {qualified_contract}")

        # Set market data type directly (expects 1–4)
        if marketDataType not in [1, 2, 3, 4]:
            raise HTTPException(status_code=400, detail=f"Invalid marketDataType: {marketDataType}")
        ib.reqMarketDataType(marketDataType)

        # Request snapshot market data
        ib.reqMktData(qualified_contract, '', snapshot=True, regulatorySnapshot=False)

        await asyncio.sleep(1)

        ticker = ib.ticker(qualified_contract)
        ib.cancelMktData(qualified_contract)

        if ticker and ticker.marketDataType != 0 and (ticker.bid != -1 or ticker.ask != -1 or ticker.last != -1):
            ticker_dict = {
                "contract": qualified_contract.nonDefaults(),
                "time": ticker.time.isoformat() if ticker.time else None,
                "bidSize": ticker.bidSize,
                "bid": ticker.bid,
                "ask": ticker.ask,
                "askSize": ticker.askSize,
                "last": ticker.last,
                "lastSize": ticker.lastSize,
                "volume": ticker.volume,
                "open": ticker.open,
                "high": ticker.high,
                "low": ticker.low,
                "close": ticker.close if not pd.isna(ticker.close) else None,
            }
            ticker_dict_filtered = {k: v for k, v in ticker_dict.items() if v is not None and not (isinstance(v, float) and pd.isna(v))}
            return {"status": "ok", "ticker": ticker_dict_filtered}
        else:
            logger.warning(f"No valid market data received for {qualified_contract}. Ticker: {ticker}")
            return {"status": "nodata", "message": "No market data available for the contract at this time.", "ticker": None}

    except ValueError as ve:
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching tick data for {secType} ({conId=}, {symbol=}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")




@app.get("/data/historical/{secType}")
async def get_historical_data(
    secType: str,
    durationStr: str = Query(..., description="Duration (e.g., '1 Y', '3 M', '60 D', '1 W')"),
    barSizeSetting: str = Query(..., description="Bar size (e.g., '1 day', '1 hour', '5 mins', '1 min')"),
    whatToShow: str = Query(..., description="Data type (e.g., 'TRADES', 'MIDPOINT', 'BID', 'ASK', 'BID_ASK')"),
    conId: int = Query(None, description="Contract ID (recommended)"),
    symbol: str = Query(None, description="Symbol (if conId not provided)"),
    exchange: str = Query(None, description="Exchange (if conId not provided)"),
    currency: str = Query("USD", description="Currency"),
    useRTH: bool = Query(True, description="Use Regular Trading Hours only"),
    formatDate: int = Query(1, description="Format date (1=yyyyMMdd HH:mm:ss, 2=epoch seconds)"),
):
    """Get historical bar data for a given contract."""
    if not ib.isConnected():
        raise HTTPException(status_code=503, detail="Not connected to IB")

    try:
        contract = create_contract(secType=secType.upper(), conId=conId, symbol=symbol, exchange=exchange, currency=currency)
        logger.info(f"Requesting historical data for: {contract} ({durationStr}, {barSizeSetting}, {whatToShow})")

        # Qualify the contract first (optional but recommended)
        qualified_contracts = await ib.qualifyContractsAsync(contract)
        if not qualified_contracts:
            raise HTTPException(status_code=404, detail=f"Contract not found or ambiguous: {contract}")
        qualified_contract = qualified_contracts[0]
        logger.info(f"Qualified contract: {qualified_contract}")

        # Request historical data
        bars = await ib.reqHistoricalDataAsync(
            qualified_contract,
            endDateTime='', # Empty means current time
            durationStr=durationStr,
            barSizeSetting=barSizeSetting,
            whatToShow=whatToShow.upper(),
            useRTH=useRTH,
            formatDate=formatDate,
            keepUpToDate=False # Set to True for streaming updates (requires different handling)
        )

        if bars:
            # Convert bars (list of BarData) to DataFrame, then to list of dicts
            df = util.df(bars)
            # Ensure datetime column is handled correctly if formatDate=1
            if formatDate == 1 and 'date' in df.columns:
                 df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None).astype(str) # Convert to string ISO format UTC? Or keep as is? Let's use string.
            elif formatDate == 2 and 'date' in df.columns:
                 df['date'] = df['date'].astype(int) # Keep as epoch seconds

            bars_list = df.to_dict(orient='records')
            return {"status": "ok", "contract": qualified_contract.nonDefaults(), "bars": bars_list}
        else:
            logger.warning(f"No historical data received for {qualified_contract} with specified parameters.")
            return {"status": "nodata", "message": "No historical data available for the contract with the specified parameters.", "bars": []}

    except ValueError as ve:
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching historical data for {secType} ({conId=}, {symbol=}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Add more endpoints here for orders, positions etc.

# Note: ib_async uses its own event loop management when using connectAsync/runAsync.
# Uvicorn will run the FastAPI app in its own loop. Communication should be handled carefully.
# Consider running ib.run() in a separate thread or process if needed,
# but connectAsync is generally preferred for integration.
