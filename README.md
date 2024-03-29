Социальная сеть YaTube для публикации постов и картинок
=====

Описание проекта
----------

Социальная сеть для авторов и подписчиков. Пользователи могут подписываться на избранных авторов, оставлять и удалять комментари к постам, оставлять новые посты на главной странице и в тематических группах, прикреплять изображения к публикуемым постам. Реализована админка на Django

Реализована система регистрации новых пользователей, восстановление паролей пользователей через почту, система тестирования проекта на unittest, пагинация постов и кэширование страниц.

Системные требования
----------
* Python 3.7+
* Works on Linux, Windows, macOS

Стек технологий
----------
* Python 3.7
* Django 2.2 
* Unittest
* Pytest
* SQLite
* CSS
* HTML

Как запустить проект:
----------

1. Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone git@github.com:Komappp/Yatube.git

cd yatube
```
2. Cоздать и активировать виртуальное окружение:
```bash
python3 -m venv venv

source venv/bin/activate
```
3. Установить зависимости из файла ```requirements.txt```:
```bash
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```
4. Выполнить миграции:
```bash
cd hw05_final

python3 manage.py migrate
```
5. Запустить проект (в режиме сервера Django):
```bash
python3 manage.py runserver
```
## Для данного проекта реализован API:
https://github.com/Komappp/api_final_yatube
