1. Установить в venv необходимые зависимости

```sh
pip install requests beautifulsoup4 langchain sentence-transformers
```

2. Выполнить скрипт для загрузки и очистки базы знаний

```sh
python Task2\fetch_pages.py
```
Будет примерно такой вывод:
```shell
python Task2\fetch_pages.py
  ok: Stargate (movie) -> stargate_movie.txt (31601 символов)
  ok: Stargate -> stargate.txt (60427 символов)
  ok: Earth -> earth.txt (24440 символов)
  ok: Jack O'Neill -> jack_o_neill.txt (67467 символов)
  ok: Daniel Jackson -> daniel_jackson.txt (68646 символов)
  ok: Samantha Carter -> samantha_carter.txt (57195 символов)
  ok: Teal'c -> teal_c.txt (52836 символов)
  ok: George Hammond -> george_hammond.txt (26457 символов)
  ok: Janet Fraiser -> janet_fraiser.txt (26579 символов)
  ok: Goa'uld -> goa_uld.txt (31026 символов)
  ok: Apophis -> apophis.txt (22945 символов)
  ok: Jaffa -> jaffa.txt (19434 символов)
  ok: Tok'ra -> tok_ra.txt (19729 символов)
  ok: Asgard -> asgard.txt (25255 символов)
  ok: Ancients -> ancients.txt (23481 символов)
  ok: Replicators -> replicators.txt (24937 символов)
  ok: Ori -> ori.txt (10539 символов)
  ok: Nox -> nox.txt (23163 символов)
  -- пропуск (после очистки документ короче 200 символов): Tollan
  ok: Stargate Command -> stargate_command.txt (22432 символов)
  ok: Dial Home Device -> dial_home_device.txt (11000 символов)
  ok: SG-1 -> sg_1.txt (26730 символов)
  ok: Puddle Jumper -> puddle_jumper.txt (28161 символов)
  ok: Milky Way -> milky_way.txt (16487 символов)
  ok: John Sheppard -> john_sheppard.txt (116195 символов)
  ok: Rodney McKay -> rodney_mckay.txt (82425 символов)
  ok: Teyla Emmagan -> teyla_emmagan.txt (67695 символов)
  ok: Ronon Dex -> ronon_dex.txt (54201 символов)
  ok: Elizabeth Weir -> elizabeth_weir.txt (60317 символов)
  ok: Wraith -> wraith.txt (47043 символов)
  ok: Atlantis -> atlantis.txt (42429 символов)
  ok: Lantean -> lantean.txt (8996 символов)
  ok: Zero Point Module -> zero_point_module.txt (18250 символов)
  ok: Pegasus -> pegasus.txt (15524 символов)
  ok: Nicholas Rush -> nicholas_rush.txt (39899 символов)
  ok: Everett Young -> everett_young.txt (13292 символов)
  ok: Eli Wallace -> eli_wallace.txt (33691 символов)
  ok: Destiny -> destiny.txt (34693 символов)
  ok: Lucian Alliance -> lucian_alliance.txt (16510 символов)

Сбор завершён. Загружено 38 страниц в raw_pages/
```


3. фывыфв