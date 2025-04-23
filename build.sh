echo
pipenv install

echo
pipenv run python manage.py collectstatic --noinput

echo
pipenv run python manage.py migrate
