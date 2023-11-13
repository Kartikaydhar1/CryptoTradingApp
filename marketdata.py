import requests
import time
import csv


def read_api_key_from_file(file_path):
    with open(file_path, 'r') as file:
        api_key = file.read().strip()
    return api_key


def make_api_request(api_key, symbols):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    params = {
        "symbol": symbols,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        response_data = response.json()
        if 'data' in response_data:
            return response_data['data']
        else:
            print("No 'data' object found in the response.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def extract_fields(response_data):
    extracted_data = {}
    for symbol, data in response_data.items():
        if 'quote' in data and 'USD' in data['quote']:
            quote = data['quote']['USD']
            price = quote.get('price')
            extracted_data[symbol] = {'symbol': symbol, 'price': price}
    return extracted_data


def poll_price(api_key, symbols):
    response_data = make_api_request(api_key, symbols)
    if response_data:
        extracted_fields = extract_fields(response_data)
        return extracted_fields
    return None


def calculate():
    api_key_file_path = "api_key.txt"
    symbols = "BTC,ETH,SOL"

    while True:
        api_key = read_api_key_from_file(api_key_file_path)
        polled_data = poll_price(api_key, symbols)

        if polled_data:
            with open("exchange_data.csv", "r") as file:
                reader = csv.reader(file)
                last_prices = {row[0]: float(row[1]) for row in reader}

            for symbol, info in polled_data.items():
                price = info["price"]
                last_price = last_prices.get(symbol)

                if last_price is not None:
                    if price > last_price:
                        print(f"Symbol: {symbol}, Action: Sell. Polled price ({price}) is greater than the last price ({last_price})")
                    else:
                        print(f"Symbol: {symbol}, Action: Buy. Polled price ({price}) is less than the last price ({last_price})")

                last_prices[symbol] = price

            with open("exchange_data.csv", "w", newline="") as file:
                writer = csv.writer(file)
                for symbol, price in last_prices.items():
                    writer.writerow([symbol, price])

        time.sleep(60)


calculate()