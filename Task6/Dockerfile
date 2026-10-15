FROM task4-ragservice
RUN apt-get update && apt-get install -y --no-install-recommends cron && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir langchain-text-splitters
COPY Task6/indexer.cron /etc/cron.d/indexer
RUN chmod 0644 /etc/cron.d/indexer && echo >> /etc/cron.d/indexer && crontab /etc/cron.d/indexer
CMD ["cron", "-f"]