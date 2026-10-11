1. Установить в venv необходимые зависимости

```shell
pip install requests beautifulsoup4 langchain sentence-transformers
```

2. Выполнить скрипт для загрузки и очистки базы знаний

```shell
python Task2\fetch_pages.py
```
Будет примерно такой вывод:
```shell
  ok: Stargate (movie) -> stargate_movie.txt (8040 символов)
  ok: Stargate -> stargate.txt (43520 символов)
  ok: Earth -> earth.txt (15639 символов)
  ok: Jack O'Neill -> jack_o_neill.txt (59995 символов)
  ok: Daniel Jackson -> daniel_jackson.txt (62335 символов)
  ok: Samantha Carter -> samantha_carter.txt (48511 символов)
  ok: Teal'c -> teal_c.txt (46235 символов)
  ok: George Hammond -> george_hammond.txt (23044 символов)
  ok: Janet Fraiser -> janet_fraiser.txt (24096 символов)
  ok: Apophis -> apophis.txt (20365 символов)
  ok: Goa'uld -> goa_uld.txt (26221 символов)
  ok: Jaffa -> jaffa.txt (14816 символов)
  ok: Tok'ra -> tok_ra.txt (17912 символов)
  ok: Asgard -> asgard.txt (22866 символов)
  ok: Ancients -> ancients.txt (19201 символов)
  ok: Replicators -> replicators.txt (22845 символов)
  ok: Ori -> ori.txt (8633 символов)
  ok: Nox -> nox.txt (22757 символов)
  ok: Tollan (people) -> tollan_people.txt (9794 символов)
  ok: Tollan (planet) -> tollan_planet.txt (6394 символов)
  ok: SG-1 -> sg_1.txt (26611 символов)
  ok: Stargate Command -> stargate_command.txt (16430 символов)
  ok: Dial Home Device -> dial_home_device.txt (10079 символов)
  ok: Puddle Jumper -> puddle_jumper.txt (24699 символов)
  ok: Milky Way -> milky_way.txt (8033 символов)
  ok: John Sheppard -> john_sheppard.txt (110639 символов)
  ok: Rodney McKay -> rodney_mckay.txt (76192 символов)
  ok: Teyla Emmagan -> teyla_emmagan.txt (65252 символов)
  ok: Ronon Dex -> ronon_dex.txt (51886 символов)
  ok: Elizabeth Weir -> elizabeth_weir.txt (56525 символов)
  ok: Wraith -> wraith.txt (43690 символов)
  ok: Atlantis -> atlantis.txt (38139 символов)
  ok: Lantean -> lantean.txt (8967 символов)
  ok: Zero Point Module -> zero_point_module.txt (16220 символов)
  ok: Pegasus -> pegasus.txt (11733 символов)
  ok: Nicholas Rush -> nicholas_rush.txt (38008 символов)
  ok: Everett Young -> everett_young.txt (11292 символов)
  ok: Eli Wallace -> eli_wallace.txt (30922 символов)
  ok: Destiny -> destiny.txt (31028 символов)
  ok: Lucian Alliance -> lucian_alliance.txt (16417 символов)

Сбор завершён. Загружено 40 страниц в raw_pages/
```
Также создастся папка `raw_pages` с содержимым

3. Выполнить скрипт для замены ключевых терминов

```shell
python Task2\apply_terms.py
```
Ожидается примерно такой вывод:
```shell
  [ref] O'Neill -> nar (of Jack O'Neill)
  [ref] O'Neills -> nar (of Jack O'Neill)
  [ref] Jackson -> keth (of Daniel Jackson)
  [ref] Carter -> rynn (of Samantha Carter)
  [ref] Vala -> Cyn (of Vala Mal Doran)
  [ref] Jonas -> Sel (of Jonas Quinn)
  [ref] Sheppard -> ryker (of John Sheppard)
  [ref] McKay -> Nar (of Rodney McKay)
  [ref] Rodney -> Kae (of Rodney McKay)
  [ref] Teyla -> Jor (of Teyla Emmagan)
  [ref] Ronon -> Ael (of Ronon Dex)
  [ref] Weir -> solen (of Elizabeth Weir)
  [ref] collision on 'rynn': 'Nicholas Rush' renamed Mal rynn -> Tal Reeve
  [ref] Rush -> Reeve (of Nicholas Rush)
  [ref] Young -> skov (of Everett Young)
=== STATS ===
  Wraith -> Zhathar: 1052
  Atlantis -> Tor Reach: 803
  Stargate -> Kestrel: 617
  Earth -> Vor March: 612
  McKay -> Nar: 564
  SG-1 -> Kestrel-1: 526
  Sheppard -> ryker: 520
  Teal'c -> Hal crowe: 475
  Goa'uld -> Jordune: 465
  O'Neill -> nar: 403
  Destiny -> Dorrynn: 333
  Ronon -> Ael: 325
  Apophis -> Zha voss: 307
  Rush -> Reeve: 304
  Carter -> rynn: 280
  Teyla -> Jor: 277
  Asgard -> Galnar: 264
  Jaffa -> Ishreeve: 225
  John Sheppard -> Zor ryker: 209
  Rodney McKay -> Kae Nar: 209
  [codes of planets recorded]: 68

Not found (14): ['dial home device', 'Stargate (movie)', "Chappa'ko", 'Recall device', 'Inverted phase communicator', "Re'tu", 'Reetalia', 'ribbon device', 'Phase-shifting weapon', 'unas', "Unas'", 'National Institute of Defense', 'Point of origin', 'BC-301']

Transformation done: 40 docs in knowledge_base/
```
Также создастся папка `knowledge_base` с содержимым (базой знаний) и скопируется файл `terms_map.json`

4. Проверить базу знаний на нахождение в них терминов, которые должны были быть заменены

```shell
python Task2\check_terms.py
```

Ожидается, что никаких терминов выведено не будет:
```shell
======================================================================
Summary
======================================================================
Files count: 40
Files affected: 0 (0.0%)
Terms found: 0 of 102
Entries count: 0

All clear
```