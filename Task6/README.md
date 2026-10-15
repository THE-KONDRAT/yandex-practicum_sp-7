Запуск

1. Создать индекс

set RAG_KB_DIR=Task6/knowledge_base
set RAG_CHROMA_DIR=Task6/index/chroma_db_v2
python Task3\build_index.py

2. Запустить бот и инициализировать средство автообновления
Выполнение из Task4
```shell
cd Task4
```

```shell
docker compose -f docker-compose.yaml -f ../Task6/docker-compose.yaml up -d --build indexer
```
```shell
docker compose -f docker-compose.yaml -f ../Task6/docker-compose.yaml exec indexer python Task6/update_index.py --init-state
```

3. Перед добавлением данных можно задать боту вопрос о сущности, которой ещё нет в базе знаний, но которая присутствует в новом файле.
Для документа `naquadria_raw.txt` это `What is Naquadria?`


4. Добавление новых данных
Сначала создать папку, если её нет
```shell
mkdir Task6\raw_new
```
Добавить файл (на примере `naquadria_raw.txt`)
Скопировать файл `naquadria_raw.txt` в `Task6\raw_new`.
Запустить скрипт переиндексации (или подождать до времени исполнения, или заменить cron-файл)
```shell
docker compose -f docker-compose.yaml -f ../Task6/docker-compose.yaml exec indexer python Task6/update_index.py
```
Ожидается вывод с такими примерно строками:
```shell
2026-10-14 23:28:35,654 INFO indexed naquadria_raw.txt: 26 chunks
2026-10-14 23:28:35,680 INFO update finished in 73.9s: 26 new chunks, index size=3367, errors=0
```

5. Проверка: задать вопросы, соответствующие новому документу