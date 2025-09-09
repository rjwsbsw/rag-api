#!/bin/bash

# PostgreSQL Container stoppen
docker-compose stop postgres

# Volume sichern
docker run --rm \
  -u $(id -u):$(id -g) \
  -v pg-data:/data:ro \
  -v "$(pwd):/backup" \
  alpine \
  sh -c "cd /data && tar czf /backup/pg-data-backup.tar.gz ."

# Container wieder starten
docker-compose start postgres