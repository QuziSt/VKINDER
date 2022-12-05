# VKINDER
### Для запуска бота необходимо:
1. Установить все сторонние библиотеки из файла ```requirements.txt```
2. Создать базу данных с именем ```netology_k```
3. Создать файл ```token.ini``` и прописать в него:
```
[VK]
vk_group_token = токен группы
vk_app_token = токен вашего приложения

[PG]
PG_USER = Имя пользователя БД
PG_PASSWORD = Пароль пользователя БД
SERVER = localhost
PORT = 5432
DB_NAME = netology_k
```
4. Добавить бота в группу используя [инструкцию](https://github.com/netology-code/adpy-team-diplom/blob/main/group_settings.md)
### Запуск бота:
Бот запускается через файл ```main.py```