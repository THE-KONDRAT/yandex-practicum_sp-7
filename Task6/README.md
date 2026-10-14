Запуск

1. Создать индекс

set RAG_KB_DIR=Task6/knowledge_base
set RAG_CHROMA_DIR=Task6/index/chroma_db_v2
python Task3\build_index.py

2. Инициализация
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
Перед добавлением данных можно задать боту вопрос о сущности, которой ещё нет в базе знаний, но которая присутствует в новом файле.
Для документа `naquadria_raw.txt` это `What is Naquadria?`
Для документа `mini_stargate_raw.txt` это `What is Mini Stargate?`

3. Добавление новых данных
Сначала создать папку, если нет
```shell
mkdir Task6\raw_new
```
Добавить файл (на примере `naquadria_raw.txt`)
Скопировать файл `naquadria_raw.txt` в `Task6\raw_new`.
Запустить скрипт подстановки терминов и перемещения файла в базу знаний
```shell
python Task2\apply_terms.py --raw-dir Task6/raw_new --out-dir Task6/knowledge_base --terms-out Task6/terms_map.json --no-clear
```
Запустить скрипт переиндексации (или подождать до времени исполнения, или заменить cron-файл)
```shell
docker compose -f docker-compose.yaml -f ../Task6/docker-compose.yaml exec indexer python Task6/update_index.py
```
4. Проверка: задать вопросы, соответствующие новому документу