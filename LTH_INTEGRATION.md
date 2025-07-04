# Life Time High (LTH) Integration

## Overview

This document explains the new LTH (Life Time High) integration in the swing trader project.

## New Components

### 1. Core App

- **Purpose**: Shared app containing LTH models and utilities
- **Location**: `core/`
- **Main Model**: `StockLTH` - stores highest ever closing price for each stock

### 2. LTH Model (`core/models.py`)

- `symbol`: Stock symbol (unique)
- `lth_price`: Highest closing price ever recorded
- `lth_date`: Date when LTH was achieved
- `last_updated`: When record was last updated
- `universe`: Which universe/category the stock belongs to

### 3. Management Command (`core/management/commands/process_lth.py`)

- **Command**: `python manage.py process_lth`
- **Purpose**: Process all stocks and store their LTH prices
- **Options**:
  - `--update-only`: Only update existing records with recent data (faster)
  - `--days-back N`: Number of days to look back for updates (default: 30)

### 4. Helper Utilities (`core/utils.py`)

- `LTHHelper`: Utility class for LTH operations
- Methods:
  - `get_lth_price(symbol)`: Get LTH price for a symbol
  - `get_lth_data(symbol)`: Get complete LTH data
  - `calculate_distance_from_lth(current_price, symbol)`: Calculate % distance from LTH
  - `is_near_lth(current_price, symbol, threshold_pct)`: Check if price is near LTH
  - `get_lth_bulk(symbols)`: Efficient bulk lookup for multiple symbols

## Updated Flow

### Initial Setup (Full Data Processing)

```bash
python manage.py makemigrations core
python manage.py migrate
python manage.py process_lth
python manage.py process_stocks
python manage.py process_ma_stocks
```

### Regular Updates (Fast)

```bash
python manage.py process_lth --update-only --days-back 7
python manage.py process_stocks
python manage.py process_ma_stocks
```

### Scripts

- `cmd.sh`: Full processing including LTH
- `update_lth.sh`: Fast LTH updates only

## Integration in Apps

### MA App Integration

- **View**: `ma/views.py` now includes LTH data in context
- **Template**: Updated to show:
  - LTH Price
  - Distance from LTH (%)
  - Near LTH indicator (within 10%)
- **Features**: Color coding based on distance from LTH

### Signals App Integration

- **Model**: Added methods to `Signal` model:
  - `get_lth_data()`: Get LTH data for signal's symbol
  - `get_distance_from_lth()`: Calculate distance using buy_price
  - `is_near_lth(threshold_pct)`: Check if near LTH

## Usage Examples

### In Views/Templates

```python
from core.utils import LTHHelper

# Get LTH data for a symbol
lth_data = LTHHelper.get_lth_data('AAPL')

# Calculate distance from LTH
distance = LTHHelper.calculate_distance_from_lth(150.0, 'AAPL')

# Check if near LTH (within 5%)
is_near = LTHHelper.is_near_lth(150.0, 'AAPL', 5.0)

# Bulk lookup for multiple symbols
symbols = ['AAPL', 'GOOGL', 'MSFT']
lth_data = LTHHelper.get_lth_bulk(symbols)
```

### In Models

```python
# For a Signal instance
signal = Signal.objects.get(id=1)
lth_data = signal.get_lth_data()
distance = signal.get_distance_from_lth()
is_near = signal.is_near_lth(threshold_pct=5.0)
```

## Performance Considerations

### Fast Updates

- Use `--update-only` flag for regular updates
- Only processes recent data (configurable days back)
- Much faster than full historical processing

### Bulk Operations

- Use `get_lth_bulk()` for multiple symbols
- More efficient than individual lookups
- Reduces database queries

### Indexing

- Symbol field is indexed for fast lookups
- Universe field is indexed for filtering

## Data Flow

1. **LTH Processing**: `process_lth` command processes all stocks and finds their LTH
2. **Strategy Processing**: `process_stocks` and `process_ma_stocks` run as usual
3. **Display Integration**: Views automatically include LTH data and calculations
4. **Template Display**: Templates show LTH information alongside signals

## Future Enhancements

1. **Real-time Updates**: Could add webhook/scheduler for daily LTH updates
2. **Alert System**: Notify when stocks approach their LTH
3. **Historical Analysis**: Track how often stocks revisit their LTH
4. **Strategy Integration**: Use LTH data in trading strategies
5. **API Endpoints**: Expose LTH data via REST API

## Configuration

The LTH processor uses the same `stocks_config.json` file as other commands, processing both 'files' and 'ma' sections to ensure all universes are covered.
