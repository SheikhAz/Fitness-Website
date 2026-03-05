echo "BUILD START"

pip install -r requirement.txt

python manage.py collectstatic --noinput --clear

echo "BUILD END"