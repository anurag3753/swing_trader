from django.core.management.base import BaseCommand
from tradewise.quotes import StockReader
from signals.models import Signal
from tradewise.strategy import V20Strategy
import datetime
import json


universe_strategies = {
    "v40": [
        {"name": "v20", "args": {"num_days": 30}},  # Example: Strategy name and its arguments
    ],
    "v40next": [
        {"name": "v20", "args": {"num_days": 20}},  # Another example
        # {"name": "MAStrategy", "args": {"window_size": 50}},
    ],
    "v200": [
        {"name": "v20", "args": {"num_days": 30}},
    ]
    # Add more mappings as needed
}

class Command(BaseCommand):
    help = 'Process stocks and store results in the database'

    def handle(self, *args, **options):
        with open('stocks_config.json', 'r') as f:
            config_data = json.load(f)

        for file_data in config_data['files']:
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

        strategy_processor = StrategyProcessor(stock_quotes, self.category)
        signals = strategy_processor.apply_strategies()

        signal_storer = SignalStorer()
        signal_storer.store_signals(signals)

class StrategyProcessor:
    def __init__(self, stock_quotes, category):
        self.stock_quotes = stock_quotes
        self.category = category

    def apply_strategies(self):
        signals = []
        strategies = universe_strategies[self.category]
        for strategy_info in strategies:
            strategy_name = strategy_info["name"]
            strategy_args = strategy_info["args"]

            strategy_class = self.get_strategy_class(strategy_name)

            # Dynamically call the strategy method based on strategy name
            strategy_method = getattr(strategy_class(self.stock_quotes, category=self.category), f"{strategy_name.lower()}_strategy")
            strategy_results = strategy_method(**strategy_args)

            for symbol, results in strategy_results.items():
                for result in results:
                    signals.append({
                        "symbol": symbol,
                        "date": result["date"],
                        "buy_price": result["buy"],
                        "sell_price": result["sell"],
                        "expected_gain": result["expected_gain"],
                        "strategy": strategy_name,
                        "universe": self.category
                    })

        return signals

    def get_strategy_class(self, strategy_name):
        # Implement logic to get the strategy class based on the name
        if strategy_name == "v20":
            return V20Strategy
        # elif strategy_name == "AnotherStrategy":
        #     return AnotherStrategy
        # Add more strategy classes as needed

class SignalStorer:
    def store_signals(self, signals):
        for signal_data in signals:
            Signal.objects.create(**signal_data)
