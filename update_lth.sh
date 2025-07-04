# Fast LTH update script - only updates with recent data
source /home/anurag3753/venv/bin/activate && cd /home/anurag3753/swing_trader && python manage.py process_lth --update-only --days-back 7
