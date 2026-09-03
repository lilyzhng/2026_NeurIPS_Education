#!/bin/bash
# Run the L073 creative-writing prompt on all four lanes, in parallel apps.
# One server one client per lane (failures.md R9). Stops every app at the end.
set -u
cd "$(dirname "$0")"

WS=lilyzhng
LOGS="$(pwd)/logs"; mkdir -p "$LOGS"
LANES="${LANES:-vanilla eagle3 dspark}"  # dflash runs offline (modal_dflash_offline.py, e2e recipe)

for lane in $LANES; do
  APP="neurips-spec-lab-$lane"
  echo "== deploy $lane -> $APP"
  env APP_NAME="$APP" SPEC_MODE="$lane" \
    uvx --with modal modal deploy modal_vllm_serve.py > "$LOGS/deploy_$lane.log" 2>&1 &
done
wait
echo "== all deployed, polling readiness (cold start ~5-8 min)"

for lane in $LANES; do
  URL="https://$WS--neurips-spec-lab-$lane-serve.modal.run"
  ok=0
  for i in $(seq 1 60); do
    if curl -sf --max-time 10 "$URL/v1/models" > /dev/null 2>&1; then ok=1; break; fi
    sleep 15
  done
  if [ "$ok" = 1 ]; then
    echo "== $lane READY, draining 45s then warmup + generate"
    sleep 45
    # first request pays CUDA-graph/compile warmup; burn it on a throwaway
    curl -sf --max-time 300 "$URL/v1/chat/completions" -H "Content-Type: application/json" \
      -d '{"model":"default","messages":[{"role":"user","content":"Say hi."}],"max_tokens":32}' > /dev/null
    python3 generate_creative_task.py --url "$URL" --label "$lane"
  else
    echo "!! $lane never became ready, skipping"
  fi
  uvx --with modal modal app stop -y "neurips-spec-lab-$lane" > /dev/null 2>&1
  echo "== $lane app stopped"
done

echo "== final app check"
uvx --with modal modal app list 2>&1 | grep -E "neurips.*deployed" || echo "all neurips apps stopped"
