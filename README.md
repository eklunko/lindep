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
или
upload_file.py http://localhost:5000/api/upload_csv mydata.csv
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


# Дополнительно

При загрузке большого .csv файла (например, 3M строк и 50 столбцов) может произойти ошибка curl:
```
curl: option --data-binary: out of memory
```
В этом случае можно попробовать использовать скрипт upload_file.py.
