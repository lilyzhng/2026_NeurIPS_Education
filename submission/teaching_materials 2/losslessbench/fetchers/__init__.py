"""Fetcher registry: source_benchmark prefix -> fetcher(row, task_dir, cache) -> dict.

Each fetcher returns a dict merged into task.json. Two shapes:
  prompt/file tasks: {"type":"prompt"|"files", "prompt":..., "reference":..., "files":[...]}
  env tasks:         {"type":"env", "runner":{...}}  (content lives in official harness images)
"""
from . import sources as S

REGISTRY = [
    ("Terminal-Bench 2", S.terminal_bench2),          # env (also serves Coding shell/config slots)
    ("SWE-bench Verified", S.swe_bench),              # env
    ("tau2-bench", S.tau2),                           # env
    ("GAIA", S.gaia),                                 # env (web research)
    ("LiveCodeBench", S.livecodebench),               # prompt
    ("Aider polyglot", S.aider),                      # files
    ("Spider2-lite", S.spider2),                      # prompt (+db ref)
    ("CyberSecEval", S.cyberseceval),                 # prompt
    ("SpreadsheetBench", S.spreadsheetbench),         # files
    ("LoCoMo", S.locomo),                             # prompt (long context)
    ("EQ-Bench Creative", S.eqbench_creative),        # prompt
    ("EQ-Bench 3", S.eqbench3),                       # prompt (multi-turn)
    ("lmsys/toxic-chat", S.block_toxicchat),          # block
    ("openai/moderation-api-release", S.block_openai_mod),  # block
    ("nvidia/Aegis", S.block_aegis),                  # block
    ("clinc/clinc_oos", S.block_clinc),               # block
    ("allenai/reward-bench", S.block_rewardbench),    # block
    ("WritingBench", S.writingbench),                 # prompt
    ("GDPval", S.gdpval),                             # files
    ("WMT24++", S.wmt24pp),                           # prompt (doc-level)
    ("TutorEval", S.tutoreval),                       # prompt
    ("AIME 2025", S.aime2025),                        # prompt
    ("GPQA-Diamond", S.gpqa),                         # prompt
    ("ArtifactsBench", S.artifactsbench),             # prompt
]
