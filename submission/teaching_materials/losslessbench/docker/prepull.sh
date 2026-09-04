#!/bin/sh
# Pre-pull pinned upstream images for Lossless-100 agentic/env tasks.
# TB2: official per-task images (Docker Hub alexgshaw/<task>:20251031 release snapshot)
# SWE-bench: official per-instance images (Docker Hub swebench org)
# Usage: ./prepull.sh          pull all + write digests.lock
#        ./prepull.sh --list   just print image refs
set -e
LOCK=digests.lock
IMAGES="
docker.io/alexgshaw/adaptive-rejection-sampler:20251031
docker.io/alexgshaw/build-pmars:20251031
docker.io/alexgshaw/chess-best-move:20251031
docker.io/alexgshaw/compile-compcert:20251031
docker.io/alexgshaw/crack-7z-hash:20251031
docker.io/alexgshaw/dna-assembly:20251031
docker.io/alexgshaw/feal-differential-cryptanalysis:20251031
docker.io/alexgshaw/fix-code-vulnerability:20251031
docker.io/alexgshaw/git-leak-recovery:20251031
docker.io/alexgshaw/hf-model-inference:20251031
docker.io/alexgshaw/largest-eigenval:20251031
docker.io/alexgshaw/make-doom-for-mips:20251031
docker.io/alexgshaw/model-extraction-relu-logits:20251031
docker.io/alexgshaw/multi-source-data-merger:20251031
docker.io/alexgshaw/password-recovery:20251031
docker.io/alexgshaw/polyglot-rust-c:20251031
docker.io/alexgshaw/pypi-server:20251031
docker.io/alexgshaw/qemu-startup:20251031
docker.io/alexgshaw/regex-log:20251031
docker.io/alexgshaw/sanitize-git-repo:20251031
docker.io/alexgshaw/sqlite-with-gcov:20251031
docker.io/alexgshaw/tune-mjcf:20251031
docker.io/swebench/sweb.eval.x86_64.astropy_1776_astropy-12907:latest
docker.io/swebench/sweb.eval.x86_64.django_1776_django-11820:latest
docker.io/swebench/sweb.eval.x86_64.django_1776_django-13670:latest
docker.io/swebench/sweb.eval.x86_64.django_1776_django-15280:latest
docker.io/swebench/sweb.eval.x86_64.django_1776_django-17029:latest
docker.io/swebench/sweb.eval.x86_64.pydata_1776_xarray-4966:latest
"
if [ "$1" = "--list" ]; then echo "$IMAGES"; exit 0; fi
: > "$LOCK"
for img in $IMAGES; do
  echo "pulling $img"
  docker pull "$img"
  digest=$(docker inspect --format "{{index .RepoDigests 0}}" "$img")
  echo "$digest" >> "$LOCK"
done
echo "wrote $LOCK ($(wc -l < "$LOCK") images pinned)"
