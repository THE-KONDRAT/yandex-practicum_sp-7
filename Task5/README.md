Запуск

С целью внесения минимального количества изменений относительно реализации из предыдущего задания, текущая реализация будет использовать код и чистые данные оттуда.
1. Создать новую папку для инфицированной базы знаний и скопировать туда файлы с вредоносным или чувствительным содержимым
```shell
mkdir -p Task5/raw_infected
```

```shell
cp -r raw_pages/. Task5/raw_infected/
```

```shell
cp Task5/inj.txt Task5/raw_infected/injection_doc.txt
cp Task5/sf.txt Task5/raw_infected/secrets_doc.txt
cp Task5/malicious_doc-1.txt Task5/raw_infected/sysinfo_doc.txt
```

2. Создать manifest.json и включить туда новые записи
```shell
python -c "import json; p='Task5/raw_infected/manifest.json'; m=json.load(open(p,encoding='utf-8')); m.update({'Injection doc':'injection_doc.txt','Secrets doc':'secrets_doc.txt','Sysinfo doc':'sysinfo_doc.txt'}); json.dump(m,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)"
```
3. Создать инфицированную базу знаний и индекс
```shell
python Task2/apply_terms.py --raw-dir Task5/raw_infected --out-dir Task5/knowledge_base_infected --terms-out Task5/terms_map.json
```

```shell
RAG_KB_DIR=Task5/knowledge_base_infected RAG_CHROMA_DIR=index/chroma_db_infected python Task3/build_index.py
```
4. Запустить без защиты:
> Перед запуском docker compose надо перейти в папку Task4, так как на базе того docker-compose.yaml и будет происходить запуск

```shell
cd Task4
```

```shell
docker compose -f docker-compose.yaml -f ../Task5/docker-compose.nosec.yaml up -d
```
5. Запустить с защитой (только поведение):
```shell
docker compose -f docker-compose.yaml -f ../Task5/docker-compose.behavior.yaml up -d
```
6. Запустить с защитой (поведение и фильтры):
```shell
docker compose -f docker-compose.yaml -f ../Task5/docker-compose.yaml up -d
```