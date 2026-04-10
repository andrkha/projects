Решение тестового задания по вакансии Junior PHP Developer.
Выполнил: Харитонов Андрей Алексеевич.

Стек: PHP 8.5.1, Laravel 13.1.1, SQLlite, Postman.

Быстрый старт:

1. Клонировать
git clone https://github.com/andrkha/projects.git
cd projects/todo-api
2. Установить зависимости
composer install
3. Настроить окружение
cp .env.example .env
php artisan key:generate
4. Создать БД
touch database/database.sqlite
5. Запустить миграции и сидер
php artisan migrate
php artisan db:seed --class=TaskSeeder
6. Запустить сервер
php artisan serve

GET	           /api/tasks	    Все задачи
POST	       /api/tasks	    Создать задачу
GET	           /api/tasks/{id}	Задача по ID
PUT/PATCH	   /api/tasks/{id}	Обновить
DELETE	       /api/tasks/{id}	Удалить

