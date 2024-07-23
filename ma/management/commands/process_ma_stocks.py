from django.core.management.base import BaseCommand
from tradewise.quotes import StockReader
from ma.models import StockSignal
from tradewise.strategy import MovingAverageStrategy
import datetime
import json

class Command(BaseCommand):
    help = 'Process stocks and store results in the database'

    def handle(self, *args, **options):
        with open('stocks_config.json', 'r') as f:
            config_data = json.load(f)

        for file_data in config_data['ma']:
            input_filename = file_data['filename']
            category = file_data['category']
            processor = StockProcessor(input_filename, category)
            processor.process_stocks()

        self.stdout.write(self.style.SUCCESS('Successfully processed and stored stocks'))

class StockProcessor:
    def __init__(self, input_filename, category):
        self.input_filename = input_filename
        self.category = category

    def process_stocks(self):
        reader = StockReader(self.input_filename)
        stocks_list = reader.read_stock_list()

        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=2*365)).strftime("%Y-%m-%d")

        stock_quotes = reader.get_stock_quotes(stocks_list, start_date, end_date)

        analyzer = MovingAverageStrategy(stock_quotes)
        signals = analyzer.moving_average_strategy()

        # Filtered Signals
        filter_signals = self.filter_signals(signals)

        # Formatted Signals
        formatted_signals = self.formatted_signals(filter_signals)
        StockSignal.objects.bulk_create([StockSignal(**signal_data) for signal_data in formatted_signals])


    def filter_signals(self, signals):
        # Read the list of stocks of interest from interest.txt
        with open('interest_ma.txt', 'r') as f:
            interested_stocks = f.read().splitlines()
        print('interested_stocks: \n', interested_stocks)

        filtered_signals = {}
        for stock, actions in signals.items():
            for action in actions:
                if action['action'] == "Buy" or (action['action'] == "Sell" and stock in interested_stocks):
                    if stock not in filtered_signals:
                        filtered_signals[stock] = []
                    filtered_signals[stock].append(action)
        return filtered_signals

    def formatted_signals(self, signals):
        formatted_signals = []
        for stock, actions in signals.items():
            for action in actions:
                formatted_signals.append({
                    "symbol": stock,
                    "date": action["date"],
                    "action": action["action"],
                    "price": action["price"],
                })

        return formatted_signals