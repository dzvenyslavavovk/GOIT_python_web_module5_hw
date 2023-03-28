import argparse
import asyncio
import logging
import platform
from datetime import datetime, timedelta

import aiohttp

CURRENCY = ['USD', 'EUR']


def command_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--days', default='1')
    return vars(parser.parse_args())


async def get_currency_request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f'Error status {response.status} for {url}')
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Connection error {url}: {e}")
        return None


async def get_currency(days):
    dates = [(datetime.now()-timedelta(days=x)).strftime('%d.%m.%Y') for x in range(days + 1)]
    exchange_rate_data = [get_currency_request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') for date in dates]
    results = await asyncio.gather(*exchange_rate_data)
    for result in results:
        if result:
            parse_currency(result)


def parse_currency(exchange_rate):
    date = exchange_rate['date']
    print(f'\n{date}:')
    for rate in exchange_rate['exchangeRate']:
        if rate['currency'] in CURRENCY:
            print(f'{rate["currency"]} SALE: {rate["saleRate"]} BUY: {rate["purchaseRate"]}')


async def main():
    args = command_parser()
    number_of_days = int(args.get('days'))
    if number_of_days > 10:
        print('The date range must be less than or equal to 10 days')
        number_of_days = 10
    await get_currency(number_of_days)


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())