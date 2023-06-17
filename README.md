# BrainForces
[![Django CI](https://github.com/fivan999/BrainForces/actions/workflows/django.yml/badge.svg)](https://github.com/fivan999/BrainForces/actions/workflows/django.yml)
[![Python package](https://github.com/fivan999/BrainForces/actions/workflows/python-package.yml/badge.svg)](https://github.com/fivan999/BrainForces/actions/workflows/python-package.yml)
## Суть проекта
Создание сайта для проведения онлайн соревновательных викторин
## Установка и запуск
### Клонировать репозиторий
```
git clone https://github.com/fivan999/BrainForces
```
### Конфигурация
Создайте .env файл в папке brainforces.<br>

В нем нужно указать значения:<br>
- SECRET_KEY (ваш секретный ключ, по умолчанию - default)<br>
- DEBUG (включать ли режим дебага, по умолчанию - True)<br>
- ALLOWED_HOSTS (если включен DEBUG, он ['*'], иначе по умолчанию - 127.0.0.1)<br>
- INTERNAL_IPS (для debug_toolbar, по умолчанию - 127.0.0.1) <br>
- LOGIN_ATTEMPTS (количество попыток входа, после которого аккаунт становится неактивным, по умолчанию - 3) <br>
- USER_IS_ACTIVE (активный ли пользователь сразу после регистрации, по умолчанию - false) <br>
- DB_NAME (имя базы данных, по умолчанию - postgres)
- DB_HOST (хост базы данных, по умолчанию - 127.0.0.1)
- DB_PORT (порт базы данных, по умолчанию - 5432)
- DB_USER (имя пользователя на сервере, по умолчанию - postgres)
- DB_PASS (пароль базы данных, по умолчанию - password)
- REDIS_HOST (хост базы данных redis, по умолчанию - localhost)
- REDIS_PORT (порт базы данных redis, по умолчанию - 6379)
- REDIS_DB=0
- ELASTICSEARCH_HOST (хост elasticsearch, по умолчанию - localhost)
- ELASTICSEARCH_PORT (порт elasticsearch, по умолчанию 9- 200)
- CELERY_TASK_ALWAYS_EAGER (выполнять ли задания от celery синхронно, запуск rabbitmq и celery не требуется при true, по умолчанию - true)
#### Настройка отправки почты
Если вы хотите, чтобы письма только сохранялись в папке sent_emails, в .env файле укажите USE_SMTP=false<br>
Иначе нужно указать несколько значений:
- USE_SMTP=True
- EMAIL_HOST (смтп, которое вы используете)
- EMAIL_PORT (порт нужного смтп)
- EMAIL_USE_TLS (true или false, по умолчанию - true), EMAIL_USE_SSL (true или false, по умолчанию - false). True должно быть только одно из двух значений
- EMAIL_HOST_USER (почта)
- EMAIL_HOST_PASSWORD (пароль от почты)
#### Настройка аутентификации через Google и Yandex
Если вы хотите, чтобы в проекте была доступна такая функция, нужно получить ключи доступа от Google и Yandex соответственно и добавить их в .env файл
- SOCIAL_AUTH_GOOGLE_OAUTH2_KEY (ключ от Google)
- SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET (секретный ключ от Google)
- SOCIAL_AUTH_YANDEX_OAUTH2_KEY (ключ от Yandex)
- SOCIAL_AUTH_YANDEX_OAUTH2_SECRET (секретный ключ от Yandex)
Пример .env файла - .env.example

## Запуск с помощью Docker (в разработке)
Скачайте Docker: https://www.docker.com/<br>
Запустите Docker<br>
В терминале:
```
docker-compose --env-file brainforces/.env build
```
```
docker-compose --env-file brainforces/.env up 
```
## Запуск без Docker
### Установка зависимостей
Создайте виртуальное окружение и активируйте его<br>
Для Windows:
```
python -m venv venv
venv\Scripts\activate
```
Для Linux:
```
python3 -m venv venv
source venv/bin/activate
```

Установите нужные зависимости

Для запуска
```
pip install -r requirements/base.txt
```
Для разработки
```
pip install -r requirements/dev.txt
```
Для тестов
```
pip install -r requirements/test.txt
```
### Запуск
Сделайте миграции:
```
python brainforces/manage.py migrate
```

Запустите проект:
```
python brainforces/manage.py runserver
```
## Использованные технологии
- База данных - PostgreSQL
- Полнотекстовый поиск с помощью elasticsearch
- Асинхронная отправка почты с помощью Celery и брокера RabbitMQ
- Redis для подсчета количества просмотров у постов
- Аутентификация с помощью Yandex и Google
## Техническое задание
В общем: cоздаем сайт для проведения онлайн соревновательных викторин
### Первый этап:
- Создать пользователя
- Создать администратора
- Создать сущности вопрос и викторина
- Для начала админ может создавать вопросы и викторины с помощью админ панели
- У викторины может быть три статуса:
  - Не начата: регистрация на викторину
  - Идет: пользователи отправляют решения (по одному на вопрос), строится табличка лидеров
  - Закончена: пользователям начисляется рейтинг, вопросы отправляются в архив, вопросы можно сдавать, пока не ответишь правильно
- Примечание: викторину создаем пока что без таймера, админ сам меняет ее статусы
- Профиль пользователя
  - Базовая информация (почта, ник, имя, фамилия, аватарка)
  - Рейтинг (можно добавить звание как на кфе в зависимости от рейтинга)
  - В каких соревнованиях участвовал (отдельная страничка)
- Главная страничка с доступными соревнованиями (добавим пагинацию)
- Страничка с архивными вопросами (также пагинация)
- Страничка с активной викториной (переключение между вопросами)
- Страничка с таблицей лидеров (пагинация)
- Страничка с конкретным вопросом
### Второй этап:
- Добавить админам возможность создавать викторину не заходя в админ-панель
- Добавить время начала и продолжительность викторины
- Добавить список лидеров
### Третий этап (возможно не успеем)
- Добавить сущность организации
  - Организация - это некая группа в нашем приложении.
  - Пользователь может создать организацию, став ее админом
  - Админ может пригласить других пользователей в организацию. Например: Данила решил создать организацию Джанго весна 23 и пригласить в нее всех джангистов.
  - Пользователь в своем профиле может принять приглашение от организации (отдельная страница)
  - И самое главное: админ организации может создавать соревнования от лица организации.
- Админ организации может посмотреть пользователей, зарегистрированных на соревнование.
- Фильтрация активных викторин по организациям
### Это мы точно вряд ли успеем, но идея хорошая
- Добавить динамическую генерацию форм для конкретного соревнования. Пояснение: пусть организация при создании соревнования хочет узнать от пользователя какие-то нужные ей данные. Например, Данила решит отправить мерч победителю викторины. Для этого ему нужны доп данные пользователя, например адрес. Эти данные сайт не будет сохранять в модели пользователя, но они будут сохраняться как дополнительные у организатора соревнования.
## Правила для разработчиков
- Тайпинг
- Одинарные кавычки (дефолт по флейку)
- У функций и классов докстринги, не обязательно документировать каждый аргумент, 
достаточно краткого описания функции
- Комментарии тоже нужны, но все подряд не комментировать, только там, где нужно)
- Нормальные и более-менее осмысленные названия классов, функций, переменных
- Отступы в шаблонах - 2 пробела. было бы славно поставить плагин djlint, чтобы
он проверял шаблоны за вас, постарайтесь максимально исправлять его исью
также полезный плагин для шаблонов - django(6,2 м. скачиваний)
- Модель ветвления такая же (ветка main, от нее ветки-фичи)
- Давать краткие и понятные комментарии к коммитам
- У полей моделей и форм обязательно писать verbose_name. help_text - очень желательно
- Для изменения виджетов формы не прописываем их в форме. Используем модуль django-widget-tweaks в шаблоне
- Все вьюхи с помощью CBV
- На функционал стараемся писать тесты
- Все тесты делаем с помощью джанговских юниттестов
- Перед коммитом проверяем, всё ли у нас хорошо
  - Проверяем линтинг с помощью flake8 и black
  - Порядок импортов с помощью isort
  - Тайпинг с помощью mypy
  - Запускаем тесты
