2021-11-26

# Сборка
```
docker compose -f docker-compose.debug.yml build
```


# Запуск
```
docker compose -f docker-compose.debug.yml up
```


# Использование
```
curl --data-binary "@mydata.csv" http://localhost:5000/api/upload_csv
```
(возвращает id задачи)

```
curl http://localhost:5000/api/running_jobs
```
(возвращает количество выполняющихся задач)

```
curl http://localhost:5000/api/job_status/6
```
(возвращает статус и результат задачи с id = 6)


# Нерешенные проблемы

1) При тестировании на большом csv файле (3M строк, 50 столбцов) - ошибка curl:
```
curl: option --data-binary: out of memory
```
Как решить, пока не знаю.
