import requests
import time


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


def poll_data(api_key, symbols, interval):
    while True:
        response_data = make_api_request(api_key, symbols)
        if response_data:
            extracted_fields = extract_fields(response_data)
            print(extracted_fields)
        time.sleep(interval)


api_key_file_path = "api_key.txt"
symbols = "BTC,ETH,SOL,XRP"
api_key = read_api_key_from_file(api_key_file_path)
poll_data(api_key, symbols, 60)