1. cp .env.sample .env
2. заполнить .env
3. docker-compose up -d --build
4. docker-compose exec app python manage.py makemigrations
5. docker-compose exec app python manage.py migrate
6. docker-compose exec app python manage.py load_fixtures
7. docker-compose exec app python manage.py createsuperuser
