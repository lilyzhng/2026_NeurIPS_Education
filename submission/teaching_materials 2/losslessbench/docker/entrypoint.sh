#!/bin/sh
# lossless100 image entrypoint
set -e
case "$1" in
  list)   ls /lossless100/hydrated/tasks ;;
  show)   cat "/lossless100/hydrated/tasks/$2/task.json" ;;
  hydrate) shift; exec python /lossless100/hydrate.py "$@" ;;   # re-hydrate/extend inside container
  prepull) exec sh /lossless100/docker/prepull.sh ;;            # print/pull pinned upstream agentic images
  export) tar -C /lossless100/hydrated -cf - tasks ;;           # stream tasks out: docker run ... export > tasks.tar
  *) exec "$@" ;;
esac
