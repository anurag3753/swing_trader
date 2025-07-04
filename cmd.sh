# redo.sh
cd /home/anurag3753/swing_trader
rm -rf db.sqlite3
source  /home/anurag3753/venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations signals
python manage.py makemigrations ma
python manage.py makemigrations core
python manage.py migrate
python manage.py process_lth
python manage.py process_stocks
python manage.py process_ma_stocks

# cmd.sh
source /home/anurag3753/venv/bin/activate && cd /home/anurag3753/swing_trader && pip install -r requirements-new.txt && python manage.py process_lth && python manage.py process_stocks && python manage.py process_ma_stocks
#source /home/anurag3753/venv/bin/activate && cd /home/anurag3753/swing_trader && pip install -r requirements.txt && python manage.py process_stocks && python manage.py process_ma_stocks
