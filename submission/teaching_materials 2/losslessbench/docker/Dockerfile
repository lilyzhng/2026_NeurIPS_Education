# Lossless-100 task image. Build with:  --build-arg DOMAIN=<slug|all>
# One image per domain (data baked at build); "all" bakes everything.
FROM python:3.13-slim-bookworm AS hydrate
ARG DOMAIN=all
WORKDIR /lossless100
COPY hydrate.py lossless100_manifest.csv ./
COPY fetchers/ fetchers/
# Bake task data at build time (network needed at build only).
# HF_TOKEN build-arg optional (public sources need none).
ARG HF_TOKEN=""
ENV HF_TOKEN=${HF_TOKEN}
RUN --mount=type=cache,target=/dlcache \
    if [ "$DOMAIN" = "all" ]; then python hydrate.py --all --out /lossless100/hydrated --cache /dlcache ; \
    elif [ "$DOMAIN" = "balanced24" ]; then python hydrate.py --suite balanced24 --out /lossless100/hydrated --cache /dlcache ; \
    else python hydrate.py --domain "$DOMAIN" --out /lossless100/hydrated --cache /dlcache ; fi

FROM python:3.13-slim-bookworm
ARG DOMAIN=all
LABEL org.opencontainers.image.source="https://github.com/lilyzhng/lily-memory" \
      org.opencontainers.image.title="Lossless-100 (${DOMAIN})" \
      org.opencontainers.image.description="Demand-proportional task suite for measuring the quality cost of accelerated LLM serving. Task data for research use; source-benchmark licenses apply (see /lossless100/hydrated/tasks/*/task.json provenance)." \
      org.opencontainers.image.licenses="CC-BY-4.0 (manifest); task content under source licenses"
WORKDIR /lossless100
COPY --from=hydrate /lossless100 /lossless100
COPY docker/prepull.sh docker/entrypoint.sh docker/
RUN chmod +x docker/*.sh
ENV LOSSLESS100_TASKS=/lossless100/hydrated/tasks
ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["list"]
