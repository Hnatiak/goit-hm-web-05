import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta

class ExchangeRateService:
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def fetch_exchange_rate(self, date):
        url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
        async with self.session.get(url) as response:
            return await response.json()

    async def get_exchange_rates(self, days):
        tasks = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
            tasks.append(self.fetch_exchange_rate(date))
        return await asyncio.gather(*tasks)

def parse_arguments():
    if len(sys.argv) != 2:
        print("Example usage: python main.py <number of days>")
        sys.exit(1)
    try:
        days = int(sys.argv[1])
        if days > 10:
            print("Error: Number of days should not exceed 10.")
            sys.exit(1)
        return days
    except ValueError:
        print("Error: Invalid input. Please enter a valid number of days.")
        sys.exit(1)

def format_exchange_rates(exchange_rates):
    formatted_rates = []
    for exchange_rate in exchange_rates:
        date = exchange_rate['date']
        print(f'\n{date}:')
        for r in exchange_rate['exchangeRate']:
            if r['currency'] in ['USD', 'EUR']:
                print(f'{r["currency"]}: sale: {r["saleRate"]}, buy: {r["purchaseRate"]}')

async def main():
    days = parse_arguments()
    async with ExchangeRateService() as exchange_rate_service:
        try:
            exchange_rates = await exchange_rate_service.get_exchange_rates(days)
            formatted_rates = format_exchange_rates(exchange_rates)
            print(formatted_rates)
        except Exception as error:
            print(f"Error: {error}")

if __name__ == "__main__":
    asyncio.run(main())