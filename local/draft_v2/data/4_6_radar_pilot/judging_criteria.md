# Judging criteria — the two new radar axes (agent, coding)

Conventions inherited from `Build/LosslessBench/JUDGING.md`: official rubrics
verbatim, win-count aggregation, tie scores one point each side, absolute
counts (X/N) as the headline, never averages.

## Agent Workflow (tau3 retail)

- **Judge = the benchmark's own reward function, no LLM judge of ours.**
  tau2-bench scores an episode by (a) DB state match against the gold final
  state after the conversation, (b) required read/write actions taken, and
  (c) NL assertions where the task defines them. Reward is 0/1 per episode.
- Controls: agent temperature 0, user simulator pinned `gpt-4o` temperature 0,
  seed 300, identical task list (retail 0-9) both arms, branch
  `fix/ab-scoring-artifacts` (post-T19 scoring fix).
- A/B aggregation: per-task winner by reward on paired episodes; equal reward
  = tie (one point each). Episodes that die of infrastructure are rerun or
  dropped from BOTH arms, never scored.
- Cross-check reported alongside: official `tau2.metrics.paired_ab`, which is
  stricter (excludes premature max_steps episodes from pairing) and adds
  action-match percentage.
- **Improvement over the frontend/creative axes**: no interactive judge and no
  rubric interpretation at all — the environment itself is the referee, so
  this axis is immune to the judge-bias failure modes logged in
  INC-2026-09-03 (T19).

## Coding (Terminal-Bench via harbor/terminus-2)

- **Judge = the task's own verifier script inside the container.** Each
  terminal-bench task ships tests that run after the agent finishes; pass/fail
  is binary, no judgment call.
- Controls: temperature 0, same 10 pinned tasks both arms (see
  `coding_results/task_ids.json`, selection rule recorded there), harbor
  terminus-2 agent, `--env modal`, k=1.
- A/B aggregation: same win-count rule. Both pass or both fail = tie.
- Caveat to print with the figure: Qwen3-8B is small for terminal-bench; if
  both arms land near 0/10 the axis records "no separation at n=10", which is
  itself the honest result. Win rate x100 feeds the radar axis either way.

## What these two axes deliberately avoid

The frontend/creative axes need an interactive judge protocol
(`interactive_judge_protocol.md`) because quality there is a rubric judgment.
Agent and coding are execution-graded: state match and tests. Any future
"improvement" to judging on these axes should stay inside the benchmarks'
official scoring, not add our own layer.
