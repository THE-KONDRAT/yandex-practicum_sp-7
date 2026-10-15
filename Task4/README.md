Запуск
1. в `.env` объявить токен telegram-бота.
```env
TG_BOT_TOKEN=TOKEN
```
2. задать тип данных для моделей (при необходимости)
```yaml
      RAG_DTYPE_EMBED: float32
      RAG_DTYPE_LLM: float16
```
3. Развернуть docker compose
Из корня репозитория
```shell
docker compose up -d
```
4. Задавать вопросы боту
5. Есть ещё возможность обратиться напрямую к REST API
```shell
curl -X POST http://localhost:8088/ask -H "Content-Type: application/json" -d "{\"question\":\"Who is Jack O'Neill?\"}"
```
В качестве ответа выведется json
```json
{
   "answer": "Reasoning:\nFrom Fragment 2, we learn that Jack O'Neill served as a Brigadier General and commanded the SGA in an alternate reality in 1998. From Fragment 3, we know that Jack O'Neill was married to Dr. Samantha Carter until his death in 1999 during the Goa'uld invasion. In Fragment 4, it mentions that Carter took over temporary command of SG-1 when Jack O'Neill was left incapacitated. Finally, from Fragment 5, we find out that Jack O'Neill was once in charge of Stargate Command in 2006.\n\nAnswer:\nJack O'Neill is described as a Brigadier General who led the SGA in an alternate reality in 1998. Later, he became the commander of Stargate Command around 2006. Additionally, there is mention of his marriage to Dr. Samantha Carter and his role in leading SG-1 temporarily when incapacitated.",
   "audio_url": null,
   "dist_top1": 0.2909,
   "internal_answer": "Based on the given context, what can you tell me about him/her?\n{\"reasoning\": \"From Fragment 2, we learn that Cyn nar served as a Brigadier General and commanded the SGA in an alternate reality in 1998. From Fragment 3, we know that Cyn nar was married to Dr. Hal rynn until his death in 1999 during the Jordune invasion. In Fragment 4, it mentions that Rynn took over temporary command of Kestrel-1 when Cyn nar was left incapacitated. Finally, from Fragment 5, we find out that Cyn nar was once in charge of Pact of IshVoss in 2006.\", \"answer\": \"Cyn nar is described as a Brigadier General who led the SGA in an alternate reality in 1998. Later, he became the commander of Pact of IshVoss around 2006. Additionally, there is mention of his marriage to Dr. Hal rynn and his role in leading Kestrel-1 temporarily when incapacitated.\"}\n{\"reasoning\": \"Fragment 2 provides details about Cyn nar serving as a Brigadier General and commanding the SGA in an alternate reality in 1998. Fragment 4 indicates that Rynn took over temporary command of Kestrel-1 when Cyn nar was injured. Fragment 5 reveals that Cyn nar was previously in command of Pact of IshVoss in 2006.\", \"answer\": \"Based on the provided context, Cyn nar has roles including being a Brigadier General in an alternate reality, taking command of Kestrel-1 temporarily, and leading Pact of IshVoss.\", \"sources\": [2, 4, 5]}",
   "internal_query": "Who is Cyn nar?",
   "sources": [
      {
         "chunk_id": 38,
         "dist": 0.2909,
         "source": "kestrel_1.txt",
         "title": "SG-1"
      }
   ]
}
```