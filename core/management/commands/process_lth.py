from django.core.management.base import BaseCommand
from tradewise.quotes import StockReader
from core.models import StockLTH
import datetime
import json


class Command(BaseCommand):
    help = 'Process stocks and store their Life Time High (LTH) closing prices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-only',
            action='store_true',
            help='Only update existing LTH records with recent data (faster)',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Number of days to look back for updates (default: 30)',
        )

    def handle(self, *args, **options):
        update_only = options['update_only']
        days_back = options['days_back']
        
        with open('stocks_config.json', 'r') as f:
            config_data = json.load(f)

        # Process all universes (both 'files' and 'ma' sections)
        all_universes = []
        
        if 'files' in config_data:
            all_universes.extend(config_data['files'])
        
        if 'ma' in config_data:
            all_universes.extend(config_data['ma'])

        total_processed = 0
        total_updated = 0
        total_new = 0

        for file_data in all_universes:
            input_filename = file_data['filename']
            category = file_data['category']
            
            self.stdout.write(f"Processing {category} universe from {input_filename}...")
            
            processor = LTHProcessor(input_filename, category, update_only, days_back)
            processed, updated, new = processor.process_lth()
            
            total_processed += processed
            total_updated += updated
            total_new += new
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"  {category}: {processed} stocks processed, {updated} LTH updated, {new} new records"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {total_processed} stocks: '
                f'{total_new} new LTH records, {total_updated} LTH records updated'
            )
        )


class LTHProcessor:
    def __init__(self, input_filename, category, update_only=False, days_back=30):
        self.input_filename = input_filename
        self.category = category
        self.update_only = update_only
        self.days_back = days_back

    def process_lth(self):
        reader = StockReader(self.input_filename)
        stocks_list = reader.read_stock_list()

        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if self.update_only:
            # For updates, only look back a few days/weeks
            start_date = (datetime.datetime.now() - datetime.timedelta(days=self.days_back)).strftime("%Y-%m-%d")
        else:
            # For initial processing, get all historical data
            start_date = (datetime.datetime.now() - datetime.timedelta(days=10*365)).strftime("%Y-%m-%d")

        stock_quotes = reader.get_stock_quotes(stocks_list, start_date, end_date)

        processed_count = 0
        updated_count = 0
        new_count = 0

        for symbol, data in stock_quotes.items():
            try:
                if data.empty:
                    continue

                # Find the highest closing price and its date
                max_close_idx = data['Close'].idxmax()
                lth_price = data.loc[max_close_idx, 'Close']
                lth_date = max_close_idx.date()

                # Update or create LTH record
                was_updated_or_new = StockLTH.update_lth_if_higher(
                    symbol=symbol,
                    price=lth_price,
                    date=lth_date,
                    universe=self.category
                )

                processed_count += 1
                
                if was_updated_or_new:
                    # Check if it's a new record or an update
                    existing_record = StockLTH.objects.filter(symbol=symbol).first()
                    if existing_record and existing_record.lth_price == lth_price:
                        if StockLTH.objects.filter(symbol=symbol).count() == 1:
                            # This was a newly created record
                            new_count += 1
                        else:
                            # This was an updated record
                            updated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {symbol}: {str(e)}")
                )

        return processed_count, updated_count, new_count
