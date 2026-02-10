import asyncio
from sync.sync_engine import run_sync
from ml.train import train_model

async def daily_job():
    await run_sync()
    train_model()

if __name__ == "__main__":
    asyncio.run(daily_job())