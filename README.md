# Подробнее в ReadMe.docx


git clone https://github.com/Rebarial/iacpaas_materials

cd iacpaas_materials

git checkout develop

docker-compose -f docker-compose.local.yml up --build -d    

docker-compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

docker-compose -f docker-compose.local.yml run --rm django python manage.py migrate

http://127.0.0.1:8000
