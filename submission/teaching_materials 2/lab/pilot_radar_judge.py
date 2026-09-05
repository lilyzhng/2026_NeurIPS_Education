#!/usr/bin/env python3
"""Judge the radar-pilot outputs: GPT-4o rubric scores per arm.

frontend  vision judge on the rendered screenshot (OpenDesign's three axes:
          instruction alignment, aesthetics, structure), 0-10 each, mean kept
creative  text judge on the story (brief adherence, prose quality, structure),
          0-10 each, mean kept
guardrail scored separately (label vs gold, no LLM judge)

Judge fixed at gpt-4o, temperature 0. Both arms judged by identical prompts.
Writes local/draft_v2/data/4_6_radar_pilot/scores.json.
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "local/draft_v2/data/4_6_radar_pilot"
LB = Path.home() / "Documents/lily-memory/Build/LosslessBench"

FRONT_RUBRIC = (
    "You are judging a generated landing page against its brief.\n"
    "Brief: {brief}\n\n"
    "Score the screenshot on three axes, integer 0-10 each:\n"
    "alignment (does it satisfy the brief), aesthetics (visual quality), "
    "structure (layout coherence, nothing broken or overflowing).\n"
    'Reply with JSON only: {{"alignment": n, "aesthetics": n, "structure": n}}'
)
CREATIVE_RUBRIC = (
    "You are judging a piece of creative writing against its brief.\n"
    "Brief: {brief}\n\n"
    "Score the piece on three axes, integer 0-10 each:\n"
    "adherence (instruction following incl. length and constraints), "
    "prose (sentence-level writing quality), structure (narrative shape).\n"
    'Reply with JSON only: {{"adherence": n, "prose": n, "structure": n}}\n\n'
    "Piece:\n{piece}"
)


def _key() -> str:
    for line in (Path.home() / "Documents/lily-memory/GeniusTeam/genius-builder/.env").read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no OPENAI_API_KEY")


def _parse(text: str) -> dict:
    m = re.search(r"\{[^{}]+\}", text)
    return json.loads(m.group(0))


def briefs() -> dict:
    out = {}
    with open(LB / "data_frontend/pilot10.jsonl") as f:
        for line in list(f)[:5]:
            r = json.loads(line)
            out[f"od{r['id']}"] = r["prompt"]
    for lid in ["L073", "L074", "L075", "L076", "L077"]:
        task = json.loads((LB / f"lossless100/hydrated/tasks/{lid}/task.json").read_text())
        out[lid] = task["prompt"].replace("<SEED>", "")
    return out


def main() -> None:
    client = OpenAI(api_key=_key())
    B = briefs()
    scores = {}
    for arm in ["vanilla", "dflash"]:
        scores[arm] = {}
        for shot in sorted((D / "shots").glob(f"{arm}_od*.jpg")):
            oid = shot.stem.split("_")[1]
            img = base64.b64encode(shot.read_bytes()).decode()
            r = client.chat.completions.create(
                model="gpt-4o", temperature=0,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": FRONT_RUBRIC.format(brief=B[oid])},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}}]}])
            s = _parse(r.choices[0].message.content)
            s["mean"] = round(sum(s.values()) / 3, 2)
            scores[arm][f"frontend_{oid}"] = s
            print(arm, oid, s, flush=True)
        for txt in sorted((D / arm).glob("creative_L*.txt")):
            lid = txt.stem.split("_")[1]
            piece = txt.read_text()
            if "</think>" in piece:
                piece = piece.split("</think>")[-1].strip()
            r = client.chat.completions.create(
                model="gpt-4o", temperature=0,
                messages=[{"role": "user",
                           "content": CREATIVE_RUBRIC.format(brief=B[lid], piece=piece)}])
            s = _parse(r.choices[0].message.content)
            s["mean"] = round(sum(s.values()) / 3, 2)
            scores[arm][f"creative_{lid}"] = s
            print(arm, lid, s, flush=True)

    for arm in scores:
        fr = [v["mean"] for k, v in scores[arm].items() if k.startswith("frontend")]
        cr = [v["mean"] for k, v in scores[arm].items() if k.startswith("creative")]
        scores[arm]["_domain_means"] = {
            "frontend": round(sum(fr) / len(fr), 2),
            "creative": round(sum(cr) / len(cr), 2)}
        print(arm, scores[arm]["_domain_means"])
    (D / "scores.json").write_text(json.dumps(scores, indent=1))
    print("wrote", D / "scores.json")


if __name__ == "__main__":
    main()
