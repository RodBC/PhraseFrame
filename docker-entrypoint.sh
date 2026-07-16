#!/bin/sh
set -eu

mkdir -p /data/documents

if [ "$(id -u)" = "0" ]; then
  chown -R phraseframe:phraseframe /data
  exec su -s /bin/sh phraseframe -c 'exec "$@"' sh "$@"
fi

exec "$@"
