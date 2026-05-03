FROM postgres:16

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    postgresql-contrib-16 \
    postgresql-16-pgvector \
 && rm -rf /var/lib/apt/lists/*
 