echo "BUILD START"
python3.9 -m pip install -r requirements.txt
python3 manage.py process_stocks
echo "BUILD END"
