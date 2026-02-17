#!/bin/sh
# wait-for-it.sh - Espera que un servicio este disponible.

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "Esperando a que $host:$port esté disponible..."
  sleep 2
done

echo "$host:$port está disponible. Ejecutando comando..."
exec $cmd