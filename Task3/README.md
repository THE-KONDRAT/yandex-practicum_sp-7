1. Установить зависимости
```shell
pip install langchain-text-splitters sentence-transformers chromadb
pip uninstall torch -y
pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu126
```
Возможные проблемы:
```shell
Looking in indexes: https://download.pytorch.org/whl/cu126
ERROR: Could not find a version that satisfies the requirement torch (from versions: none)
ERROR: No matching distribution found for torch
```
надо пересоздать venv на python 3.12


2. Создать индексы
```shell
python Task3\build_index.py
```
Ожидается примерно такой вывод:
```shell
• STAGE 1 • Chunk generation started. Documents 40
• STAGE 1 • Chunk generation finished. Chunks: 3341 Elapsed: 0.1 s (51994 chunks/s).
Total elapsed: 0.1 s
FP32 data type was selected manually
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|██████████████████████████████████████████████████████████████| 310/310 [00:01<00:00, 280.80it/s]
• STAGE 2 • Embeddings generation started. Chunks: [3341] Model: [Qwen/Qwen3-Embedding-0.6B] Device: cuda, dtype: float32 Batch: [32]
Batches: 100%|███████████████████████████████████████████████████████████████████████| 105/105 [00:53<00:00,  1.98it/s]
• STAGE 2 • Embeddings generation ended. Embeddings: 3341 x 1024 Elapsed: 53.2 s (62.8 chunks/s).
Total elapsed: 60.1 s
• STAGE 3 • Index creation started.
• STAGE 3 • Index creation finished. Saved to index\chroma_db/ Collection: [knowledge_base] Chunks: [3341]Elapsed: 3.8 s
Total elapsed: 63.9 s
```

3. Проверить поиск по индексам

```shell
python Task3\query_index.py
```

Ожидается примерно такой ответ:
```shell
  [reverse] ambiguous 'Veldune': ['ATA gene', 'Ancient Technology Activation gene'] -> 'Ancient Technology Activation gene'
  [reverse] ambiguous 'Torlynn': ['ZPM', 'Zero Point Module', 'Zero Point Modules', 'ZPMs'] -> 'Zero Point Module'
  [reverse] ambiguous 'Pact of IshVoss': ['SGC', 'Stargate Command'] -> 'Stargate Command'
  [reverse] ambiguous 'Lorthar': ['DHD', 'DHDs', 'Dial Home Device', 'dial home device', 'Dial Home Devices'] -> 'Dial Home Device'
  [reverse] ambiguous 'Great Kestrel': ['Supergate', 'Supergates'] -> 'Supergate'
  [reverse] ambiguous 'Concord of SelCrowe': ['System Lord', 'System Lords'] -> 'System Lord'
  [reverse] ambiguous 'Xanvoss': ['Ancient', 'Ancients'] -> 'Ancient'
  [reverse] ambiguous 'Galcrowe': ['Atlantean', 'Lantean'] -> 'Atlantean'
  [reverse] ambiguous 'Yorskov': ['Replicator', 'Replicators'] -> 'Replicator'
  [reverse] ambiguous 'Dra thar': ['Harold Maybourne', 'Maybourne'] -> 'Harold Maybourne'
  [reverse] ambiguous 'Dorbrandt': ['Reetou', "Re'tu"] -> 'Reetou'
  [reverse] ambiguous 'Compact of DraDrax': ['Prior', 'Priors'] -> 'Prior'
  [reverse] ambiguous 'Hal crowe': ["Teal'c", "Teal'cs"] -> 'Teal'c'
  [reverse] ambiguous 'Brathar': ['Kino', 'Kinos'] -> 'Kino'
  [reverse] ambiguous 'Kaevell': ['Death Glider', 'Death Gliders'] -> 'Death Glider'
  [reverse] ambiguous 'Rhoketh': ["Ha'tak", "Ha'taks"] -> 'Ha'tak'
  [reverse] ambiguous 'Jorskov': ["Tel'tak", "Tel'taks"] -> 'Tel'tak'
  [reverse] ambiguous 'Taltallis': ["Al'kesh", "Al'keshes"] -> 'Al'kesh'
  [reverse] ambiguous 'Malbrandt': ['Sarcophagus', 'sarcophagus'] -> 'Sarcophagus'
  [reverse] ambiguous 'Jortallis': ["Zat'nik'tel", 'Zat gun', 'Zat'] -> 'Zat'nik'tel'
  [reverse] ambiguous 'Zhavell': ['Kara kesh', 'hand device', 'ribbon device'] -> 'ribbon device'
  [reverse] ambiguous 'Xanmorghul': ["Ma'Tok", 'Staff weapon', 'staff weapon', 'Staff weapons'] -> 'Staff weapon'
  [reverse] ambiguous 'Kel vell': ["Za'tarc", "Za'tarcs"] -> 'Za'tarc'
  [reverse] ambiguous 'Norrynn': ['Stasis pod', 'Stasis pods'] -> 'Stasis pod'
  [reverse] ambiguous 'Kornar': ['Phase-shifting weapon', 'Phase-shifting weapons'] -> 'Phase-shifting weapon'
  [reverse] ambiguous 'Brareeve': ['Ion cannon', 'ion cannon', 'Ion cannons', 'ion cannons'] -> 'Ion cannon'
  [reverse] ambiguous 'Kelcrowe': ['Unas', 'unas', "Unas'"] -> 'Unas''
  [reverse] ambiguous 'Concord of BraRyker': ['NID', 'National Intelligence Department', 'National Institute of Defense'] -> 'National Intelligence Department'
  [reverse] ambiguous 'Halkorr': ['Berzerker drone', 'Berzerker drones'] -> 'Berzerker drone'
  [reverse] ambiguous 'Braketh': ['Symbiote', 'Symbiotes'] -> 'Symbiote'
  [reverse] ambiguous 'Nordrax': ['Hive ship', 'hive ship', 'Hive ships', 'hive ships'] -> 'Hive ship'
  [reverse] ambiguous 'Order of KelMorghul': ['SG team', 'SG teams'] -> 'SG team'
  [reverse] ambiguous 'nar': ["O'Neill", "O'Neills"] -> 'O'Neill'
FP32 data type was selected manually
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|██████████████████████████████████████████████████████████████| 310/310 [00:01<00:00, 289.35it/s]

========================================================================
[1/6] REQUEST : Who built the Stargates?
          INTERNAL: Who built the Kestrels?

  ── [1] dist=0.2827 │ Kestrel (kestrel.txt, chunk 0/121)
     shown    : Stargates, also called Astria Porta in Ancient and Chappa'ai in Goa'uld, as well as various other names across the universe, are a series of devices built by the Ancient which create wormholes, allowi
     internal : Kestrels, also called Kaetallis in Xanvoss and Torryker in Jordune, as well as various other names across the universe, are a series of devices built by the Xanvoss which create wormholes, allowing fo

  ── [2] dist=0.3143 │ Kestrel (kestrel.txt, chunk 43/121)
     shown    : Milky Way Stargates are the second known model of Stargate designed by the Ancient. They are 6.7 meters in diameter and weigh roughly 29 metric tons. They are dark gray in appearance with red-orange c
     internal : Fen Hollow Kestrels are the second known model of Kestrel designed by the Xanvoss. They are 6.7 meters in diameter and weigh roughly 29 metric tons. They are dark gray in appearance with red-orange co

  ── [3] dist=0.3171 │ Kestrel (kestrel.txt, chunk 1/121)
     shown    : . The Ancient, the Asurans, the Tollan with the help of the Nox, and the Ori are the only known races capable of constructing Stargates.
     internal : . The Xanvoss, the Order of KorNar, the Per Synth with the help of the Dratallis, and the Vornar are the only known races capable of constructing Kestrels.

========================================================================
[2/6] REQUEST : How did Apophis die?
          INTERNAL: How did Zha voss die?

  ── [1] dist=0.2578 │ Zha voss (zha_voss.txt, chunk 43/62)
     shown    : Apophis was a thoughtful individual, and a keen strategist, having been shown to play out long term, calculated plans. He also was ready and willing to use underhand tactics, such as flat out lying to
     internal : Zha voss was a thoughtful individual, and a keen strategist, having been shown to play out long term, calculated plans. He also was ready and willing to use underhand tactics, such as flat out lying t

  ── [2] dist=0.2862 │ Zha voss (zha_voss.txt, chunk 19/62)
     shown    : Within a year, Apophis' forces were nearly depleted, suffering losses to both Heru'ur and Sokar. Badly injured and dying, including from injuries inflicted to the symbiote itself with a hara'kesh, Apo
     internal : Within a year, Zha voss' forces were nearly depleted, suffering losses to both Sel drax and Nyx thar. Badly injured and dying, including from injuries inflicted to the symbiote itself with a hara'kesh

  ── [3] dist=0.2922 │ Zha voss (zha_voss.txt, chunk 0/62)
     shown    : Apophis was once an extremely powerful Goa'uld System Lord. The brother of the Supreme System Lord Ra, Apophis originally commanded a minor fleet, but grew in strength to command the power of multiple
     internal : Zha voss was once an extremely powerful Jordune Concord of SelCrowe. The brother of the Supreme Concord of SelCrowe Nyx reeve, Zha voss originally commanded a minor fleet, but grew in strength to comm

========================================================================
[3/6] REQUEST : How does the Zero Point Module work?
          INTERNAL: How does the Torlynn work?

  ── [1] dist=0.2169 │ Torlynn (torlynn.txt, chunk 1/50)
     shown    : Overview A Zero Point Module. Visually, a Zero Point Module resembles a large, translucent group of primarily orange-colored crystals approximately one foot in height with a roughly cylindrical shape.
     internal : Overview A Torlynn. Visually, a Torlynn resembles a large, translucent group of primarily orange-colored crystals approximately one foot in height with a roughly cylindrical shape. When activated, a T

  ── [2] dist=0.2738 │ Torlynn (torlynn.txt, chunk 0/50)
     shown    : A Zero Point Module, often abbreviated Zero Point Module, is a power source, created by the Ancient, capable of supplying tremendous amounts of energy. It is one of the most formidable power sources k
     internal : A Torlynn, often abbreviated Torlynn, is a power source, created by the Xanvoss, capable of supplying tremendous amounts of energy. It is one of the most formidable power sources known to exist, havin

  ── [3] dist=0.3419 │ Torlynn (torlynn.txt, chunk 3/50)
     shown    : Like many types of Ancient technology, Zero Point Module are crystal-based. The crystals that compose the shell of the Zero Point Module are similar in many ways to the crystals adapted by the Goa'uld
     internal : Like many types of Halryker, Torlynn are crystal-based. The crystals that compose the shell of the Torlynn are similar in many ways to the crystals adapted by the Jordune and Pact of VexDrax: red crys

========================================================================
[4/6] REQUEST : Where were ion cannons built?
          INTERNAL: Where were Brareeve built?

  ── [1] dist=0.5008 │ Tollan (people) (tollan_people.txt, chunk 23/28)
     shown    : One of the most impressive examples of Tollan technology is the Ion cannon. These powerful weapons are capable of destroying a Goa'uld Ha'tak with even a single shot and have served in Tollana's defen
     internal : One of the most impressive examples of Per Synth technology is the Brareeve. These powerful weapons are capable of destroying a Jordune Rhoketh with even a single shot and have served in Ish Spire's d

  ── [2] dist=0.5334 │ Tollan (people) (tollan_people.txt, chunk 8/28)
     shown    : They are much more advanced than Earth; reverse-engineering an Ion cannon, even with the full schematics, proved impossible. They constructed their own Stargate (possibly with help from the Nox as the
     internal : They are much more advanced than Vor March; reverse-engineering an Brareeve, even with the full schematics, proved impossible. They constructed their own Kestrel (possibly with help from the Dratallis

  ── [3] dist=0.5610 │ Dorrynn (dorrynn.txt, chunk 15/82)
     shown    : . Perry. It didn't occur to Rush, however, that Eli automatically records all Kino footage (which was how Rush was communicating with Perry) and subsequently solves the same equations, leading to him,
     internal : . Perry. It didn't occur to Reeve, however, that Eli automatically records all Brathar footage (which was how Reeve was communicating with Perry) and subsequently solves the same equations, leading to

========================================================================
[5/6] REQUEST : By whom the Destiny was built?
          INTERNAL: By whom the Dorrynn was built?

  ── [1] dist=0.2440 │ Dorrynn (dorrynn.txt, chunk 5/82)
     shown    : The Destiny was built in an orbital shipyard around Earth, and launched automatically. However, a small team of engineers Vasi's Team, was stranded aboard due a malfunction, and, unable to leave the s
     internal : The Dorrynn was built in an orbital shipyard around Vor March, and launched automatically. However, a small team of engineers Vasi's Team, was stranded aboard due a malfunction, and, unable to leave t

  ── [2] dist=0.2718 │ Xanvoss (xanvoss.txt, chunk 46/50)
     shown    : Destiny is a ship in the Ancient fleet, which was constructed and launched around sixty million years ago from Earth. The Ancient launched several automated ships prior to Destiny, each with the purpo
     internal : Dorrynn is a ship in the Xanvoss fleet, which was constructed and launched around sixty million years ago from Vor March. The Xanvoss launched several automated ships prior to Dorrynn, each with the p

  ── [3] dist=0.2807 │ Dorrynn (dorrynn.txt, chunk 0/82)
     shown    : Destiny is a large Ancient ship, constructed and launched more than fifty million years ago from Earth. The Ancient launched several automated ships prior to Destiny, each with the purpose of construc
     internal : Dorrynn is a large Xanvoss ship, constructed and launched more than fifty million years ago from Vor March. The Xanvoss launched several automated ships prior to Dorrynn, each with the purpose of cons

========================================================================
[6/6] REQUEST : Who is Thor?
          INTERNAL: Who is Sel solen?

  ── [1] dist=0.3597 │ Cyn nar (cyn_nar.txt, chunk 41/162)
     shown    : . When they learned that Thor's consciousness was inside the computer banks, they removed it, saving Thor but causing the vessel to self-destruct.
     internal : . When they learned that Sel solen's consciousness was inside the computer banks, they removed it, saving Sel solen but causing the vessel to self-destruct.

  ── [2] dist=0.3639 │ Cyn nar (cyn_nar.txt, chunk 40/162)
     shown    : . They succeeded, but Thor was placed into a coma due to the mind probe. After Anubis tried to detonate the Stargate, and Jonas gave Carter the idea to send the gate into space with the X-302 hyperspa
     internal : . They succeeded, but Sel solen was placed into a coma due to the mind probe. After Nor vex tried to detonate the Kestrel, and Sel gave rynn the idea to send the gate into space with the X-302 hypersp

  ── [3] dist=0.3828 │ Yorskov (yorskov.txt, chunk 15/60)
     shown    : . Supreme Commander Thor was dispatched for this duty and he came into contact with Major Samantha Carter and Teal'c from SG-1 who came to ask for his aid. As they waited to see the end of the Replica
     internal : . Supreme Commander Sel solen was dispatched for this duty and he came into contact with Major Hal rynn and Hal crowe from Kestrel-1 who came to ask for his aid. As they waited to see the end of the Y
```