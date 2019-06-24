Тренировочное приложение Awesome Blogs
====================

Запуск приложения
-----------

Для запуска приложения выполните (необходимы установленные git, docker, docker-machine, docker-compose):


    git clone https://github.com/theodor85/awesome_blogs.git
    cd awesome_blogs/awesome_blogs
    docker-compose -f local.yml up

Затем введите в строке браузера:

    http://0.0.0.0:8000/

Админ-панель:

    http://0.0.0.0:8000/admin

Создание суперпользователя:
------------------------

    docker-compose -f local.yml run django python manage.py createsuperuser