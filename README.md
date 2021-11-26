2021-11-26


Сборка
------

docker compose -f docker-compose.debug.yml build

Запуск
------

docker compose -f docker-compose.debug.yml up


Использование
-------------

curl --data-binary "@mydata.csv" http://localhost:5000/api/upload_csv

(возвращает id задачи)


curl http://localhost:5000/api/running_jobs

(возвращает количество выполняющихся задач)


curl http://localhost:5000/api/job_status/6

(возвращает статус и результат задачи с id = 6)



Нерешенные проблемы:
--------------------
1) При тестировании на большом csv файле (3M строк, 50 столбцов):

curl: option --data-binary: out of memory

Как решить, пока не знаю.


2) При тестировании на меньшем файле (3M строк, 5 столбцов):

rabbitmq сообщает, что превышена максимально допустимая длина сообщения:

lindep-rabbitmq-1  ... channel exception precondition_failed: message size 442045834 is larger than configured max size 134217728

Связано с тем, что у меня весь полученный текст csv файла передается в celery-задачу как аргумент задачи.
Либо надо увеличивать максимально допустимую длину сообщения rabbitmq (если это можно настроить),
либо изменить сам подход - например, сохранять полученный текст во временный файл (на стороне сервиса),
а в celery-задачу передавать ссылку на файл.
