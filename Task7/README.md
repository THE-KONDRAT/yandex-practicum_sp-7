1. Удаление ключевых сущностей

Из директории `Task7\knowledge_base` удалить:
- `vel_solen.txt`
- `kel_zyx.txt`
- `dratallis.txt`
Из manifest.json убрать соответствующие записи:
- `Elizabeth Weir`
- `Eli Wallace`
- `Nox`

2. Обновить индекс
Если бот не запущен, то запустить. Выполняется из-под Task4^:
```shell
cd Task4
```
```shell
docker compose -f docker-compose.yaml -f ../Task7/docker-compose.yaml up -d
```

3. ва