# referral_app

`posts_app` - Приложение - REST API реферальной системы. Приложение позволяет пользователям регистрироваться по номеру телефона, получать личный инвайт-код, вводить инвайт-код, полученный от другого пользователя.

Краткое описание API содержится в данном файле. Подробная документация в формате Redoc будет доступна после запуска приложения по адресу `http://<host address>/docs/`

## Системные требования
- Python 3.11+
- Works on Linux, Windows, macOS

## Основные технологии:
- Python 3.11
- Django
- Django Rest Framework
- PostgreSQL
- Celery
- RabbitMQ
- Gunicorn
- Nginx


## Как запустить проект:

Для запуска в проект вложена конфигурация docker-compose. После выполнения всех шагов запуска docker-compose документация будет доступна по адресу: `http://<host address>/docs/`.

API будет доступно по адресу `http://<host address>/api/`.

Необходимо выполнить следующие шаги:
- Склонируйте репозиторий с GitHub и перейдите в папку проекта, где расположен файл docker-compose.yml:
```
git clone git@github.com:KostKH/referral_app.git
cd posts_app/infra_referral_app
```
- Проверьте, что на машине / сервере установлены `docker` и `docker compose`

- Cоздайте в папке `infra_referral_app` файл `.env`  для хранения переменных окружения. Можно создать его из вложенного образца `env_example.env`:
```
cp env_example.env .env
```
- Откройте файл .env в редакторе и поменяйте секретный ключ приложения, а также пароли к PostgreSQL, RabbitMQ

- Установите и запустите приложение в контейнере. (Возможно, вам придется добавить `sudo` перед текстом команды):
```
docker compose up -d
```
- Запустите миграции и соберите статику:
```
docker compose exec app python manage.py migrate
docker compose exec app python manage.py collectstatic
```
- Если вы хотите использовать админку Django (доступна по адресу `http://<host address>/admin/`- тогда создайте суперпользователя:
```
docker compose exec app python manage.py createsuperuser
```
После этого приложение будет готово к работе.

## Тесты
Для запуска тестов, после того, как вы запустили приложение в докере (см.предыдущие шаги), находясь в папке `infra_referral_app`, выполните следующие команды:
```
docker compose exec app python manage.py test
```

## Основные эндпойнты у API:

`http:/<host_address>/api/users/` - GET, просмотр списка пользователей.

`http:/<host_address>/api/auth/registration/` - POST, регистрация и вход - по номеру телефона.

`http:/<host_address>/api/auth/verification/` - POST, запрос на получение токена авторизации. Нужно отправить номер телефона и полученный SMS-код.

`http:/<host_address>/api/users/<id>/` - GET, Просмотр данных пользователя <id>, а также номеров телефонов тех пользователей, которые воспользовались инвайт-кодом пользователя.

`http:/<host_address>/api/users/<id>/` - PATCH, Изменение данных пользователя <id>, ввод полученного инвайт-кода (granted_code).

## Документация по API:
После запуска сервиса документация по API будет доступна по ссылке:
- `http:/<host_address>/docs/`

## О программе:

Автор: Константин Харьков