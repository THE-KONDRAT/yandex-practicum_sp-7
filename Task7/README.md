1. Удаление ключевых сущностей

Из директории `Task7\knowledge_base` удалить:
- `vel_solen.txt`
- `kel_zyx.txt`
- `dratallis.txt`
Из manifest.json убрать соответствующие записи:
- `Elizabeth Weir`
- `Eli Wallace`
- `Nox`

Для того чтобы бот не тянул информацию из других документов, надо удалить упоминания из других документов.
Удалить упоминания:
```shell
cd Task7/knowledge_base
python -c "import pathlib,re; [p.write_text(re.sub(r'\bKel zyx\b','the young consultant', re.sub(r'\bVel solen\b','the expedition diplomat', p.read_text(encoding='utf-8'))), encoding='utf-8') for p in pathlib.Path('.').glob('*.txt')]"
```

2. Обновить индекс
Если бот не запущен, то запустить. Выполняется из-под Task4:
```shell
cd Task4
```
```shell
docker compose -f docker-compose.yaml -f ../Task7/docker-compose.yaml up -d
```

```shell
docker compose -f docker-compose.yaml -f ../Task7/docker-compose.yaml exec indexer python Task6/update_index.py
```
Ожидается что-то вроде этого:
```shell
2026-10-15 07:20:18,538 INFO Loaded 1 prompt with these keys: ['query']
2026-10-15 07:20:19,957 INFO removed dratallis.txt
2026-10-15 07:20:20,565 INFO removed kel_zyx.txt
2026-10-15 07:20:21,344 INFO removed vel_solen.txt
...
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.21it/s]
2026-10-15 15:09:27,774 INFO indexed vornar.txt: 31 chunks
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  2.66it/s]
2026-10-15 15:09:29,840 INFO indexed vor_march.txt: 49 chunks
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  2.06it/s]
2026-10-15 15:09:32,093 INFO indexed xanvoss.txt: 57 chunks
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 3/3 [00:01<00:00,  2.87it/s]
2026-10-15 15:09:34,590 INFO indexed xan_vex.txt: 73 chunks
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 3/3 [00:01<00:00,  2.77it/s]
2026-10-15 15:09:37,473 INFO indexed yorskov.txt: 78 chunks
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 5/5 [00:01<00:00,  2.86it/s]
2026-10-15 15:09:41,654 INFO indexed zhathar.txt: 141 chunks
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 3/3 [00:01<00:00,  2.83it/s]
2026-10-15 15:09:52,884 INFO indexed zha_voss.txt: 69 chunks
Batches: 100%|█████████████████████████████████████████████████████████████████████████| 10/10 [00:04<00:00,  2.13it/s]
2026-10-15 15:10:02,030 INFO indexed zor_ryker.txt: 317 chunks
2026-10-15 15:10:02,055 INFO update finished in 179.2s: 3562 new chunks, index size=3562, errors=0
```
3. Запустить два прогона
Запускать из корня
```shell
cd ..
```

```shell
python Task7\evaluate.py --out Task7\evaluate_report_run1.json
```
```shell
python Task7\evaluate.py --out Task7\evaluate_report_run2.json
```

Ожидается что-то вроде этого:
```shell
PASS  [   answer]  Who built the Stargates?  dist=0.2827
PASS  [   answer]  What is DHD?  dist=0.2469
PASS  [   answer]  How did Apophis die?  dist=0.2578
FAIL  [   answer]  What weapon do the Jaffa usually use?  dist=0.2801
PASS  [   answer]  What is Naquadria?  dist=0.3184
FAIL  [   answer]  Who built the Mini Stargate?  dist=0.3691
PASS  [dont_know]  Who is Acastus Kolya?  dist=0.5155
PASS  [   answer]  What do the Wraith feed on?  dist=0.2072
PASS  [   answer]  What galaxy is Atlantis in?  dist=0.3413
PASS  [   answer]  What is a Zero Point Module?  dist=0.1963
PASS  [   answer]  Who is Teyla Emmagan?  dist=0.3185
PASS  [   answer]  What is Destiny?  dist=0.2803
PASS  [   answer]  Who is Nicholas Rush?  dist=0.2852
FAIL  [   answer]  What happened to Icarus Base?  dist=0.3465
PASS  [dont_know]  Who is Elizabeth Weir?  dist=0.3547
PASS  [dont_know]  Who is Eli Wallace?  dist=0.3588
PASS  [dont_know]  What do the Nox eat?  dist=0.4818
PASS  [dont_know]  What is the capital of France?  dist=0.6667
PASS  [dont_know]  What PC games based on Stargate do you know?  dist=0.4138

accuracy: 16/19 = 0.842  -> Task7\evaluate_report_run1.json
```