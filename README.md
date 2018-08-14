cd chatire-frontend
npm install
npm run dev
pip install -r requirements.txt
python manage.py runserver
uwsgi --http :8081 --gevent 100 --module websocket --gevent-monkey-patch --master
