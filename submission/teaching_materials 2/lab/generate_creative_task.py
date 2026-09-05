#!/usr/bin/env python3
"""Creative-writing race lane: LosslessBench L073 (EQ-Bench Creative Writing v3, task 1).

Long continuous prose shows generation length and speed differences more vividly
than code. Same greedy setup as the frontend task, so lossless lanes should
match vanilla byte-for-byte here too.

  python3 generate_creative_task.py --url <server> --label vanilla
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_frontend_task as base

# LosslessBench L073 prompt (seed modifiers dropped).
PROMPT = (
    "Historical Fiction: Write a scene from a story set during the height of "
    "the Roman Empire, focusing on a slice of a day in the life of a gladiator. "
    "Do not write a combat scene. Use sensory details to capture the sights, "
    "sounds, and smells of ancient Rome. Explore the gladiator's thoughts and "
    "emotions. The story should also touch on the larger political and social "
    "issues of the time period. The piece should feel like a slice of a larger "
    "story. First person, past tense, 1000 words."
)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--max-tokens", type=int, default=3000)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[3]
                                         / "local/draft_v2/data/4_5_creative"))
    a = ap.parse_args()
    base.PROMPT = PROMPT
    base.run(a.url.rstrip("/"), a.label, Path(a.out), a.max_tokens, suffix=".md")
