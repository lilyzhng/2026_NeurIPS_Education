"""Concrete fetchers for the 17 Lossless-100 source benchmarks.

All network access goes through _get()/_get_json() with an on-disk cache, so
repeat hydration (and docker builds) are fast and deterministic.
"""
import csv, gzip, hashlib, io, json, os, re, tarfile, urllib.request, zipfile
from pathlib import Path

UA = {"User-Agent": "lossless100-hydrator/0.1"}
DS = "https://datasets-server.huggingface.co/rows?dataset={d}&config={c}&split={s}&offset={o}&length={n}"

def _get(url, cache: Path, binary=False):
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    p = cache / key
    if not p.exists():
        req = urllib.request.Request(url, headers=dict(UA, **(
            {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"} if os.environ.get("HF_TOKEN") and "huggingface" in url else {})))
        with urllib.request.urlopen(req, timeout=120) as r:
            p.write_bytes(r.read())
    return p.read_bytes() if binary else p.read_text(encoding="utf-8", errors="replace")

def _get_json(url, cache): return json.loads(_get(url, cache))

def _ds_rows(dataset, config, split, offset, length, cache):
    """Page through datasets-server (max 100/page)."""
    rows = []
    while length > 0:
        n = min(100, length)
        d = _ds_rows_page(dataset, config, split, offset, n, cache)
        rows += d
        if len(d) < n: break
        offset += n; length -= n
    return rows

def _ds_rows_page(dataset, config, split, offset, n, cache):
    url = DS.format(d=urllib.parse.quote(dataset, safe=""), c=config, s=split, o=offset, n=n)
    return [r["row"] for r in _get_json(url, cache).get("rows", [])]

import urllib.parse

# ---------- env-type: reuse official harnesses/images ----------

TB2_COMMIT = "69671fbaac6d67a7ef0dfec016cc38a64ef7a77c"

def terminal_bench2(row, tdir, cache):
    t = row["source_task_id"]
    instr = _get(f"https://raw.githubusercontent.com/laude-institute/terminal-bench-2/{TB2_COMMIT}/{t}/instruction.md", cache)
    (tdir / "instruction.md").write_text(instr)
    return {"type": "env", "runner": {
        "harness": "harbor", "benchmark": "terminal-bench", "version": "2.0",
        "task": t, "pin": f"laude-institute/terminal-bench-2@{TB2_COMMIT}",
        "run": f"harbor run --benchmark terminal-bench@2.0 --task {t} --agent <your-agent>",
        "note": "task env ships as official docker image resolved by harbor; pre-pull via docker/prepull.sh"}}

def swe_bench(row, tdir, cache):
    iid = row["source_task_id"]
    r = _ds_rows_page("princeton-nlp/SWE-bench_Verified", "default", "test", 0, 1, cache)  # warm check only
    image = f"docker.io/swebench/sweb.eval.x86_64.{iid.replace('__','_1776_')}:latest"
    return {"type": "env", "runner": {
        "harness": "swebench", "dataset": "princeton-nlp/SWE-bench_Verified", "instance_id": iid,
        "official_image": image,
        "run": f"python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Verified --instance_ids {iid} --predictions_path <preds.json>",
        "note": "official per-instance image; pin digest at pre-pull time (docker/prepull.sh writes digests.lock)"}}

def tau2(row, tdir, cache):
    t = row["source_task_id"]; domain = t.split(":", 1)[0]
    return {"type": "env", "runner": {
        "harness": "tau2-bench", "pip": "git+https://github.com/sierra-research/tau2-bench",
        "domain": domain, "task_id": t.split(":", 1)[1],
        "run": f"tau2 run --domain {domain} --task-ids '{t.split(':',1)[1]}' --agent-llm <model>",
        "note": "python gym, no docker needed; runs inside lossless100-runner image"}}

def gaia(row, tdir, cache):
    t = row["source_task_id"]
    rows = _ds_rows("sayan1101/gaia_filtered_text_only", "default", "validation", 0, 400, cache)
    hit = next((r for r in rows if r.get("task_id") == t), None)
    if hit is None: raise ValueError(f"GAIA task {t} not in mirror")
    (tdir / "question.txt").write_text(hit.get("Question", ""))
    return {"type": "env", "runner": {
        "harness": "web-agent", "dataset": "gaia-benchmark/GAIA (mirror: sayan1101/gaia_filtered_text_only)",
        "task_id": t, "level": hit.get("Level"),
        "question": hit.get("Question", ""), "final_answer": hit.get("Final answer", hit.get("final_answer", "")),
        "note": "browsing agent episode; scored by exact answer match"}}

# ---------- prompt-type ----------

def livecodebench(row, tdir, cache):
    qid = row["source_task_id"]
    blob = _get("https://huggingface.co/datasets/livecodebench/code_generation_lite/resolve/main/test6.jsonl", cache)
    for line in blob.splitlines():
        if not line.strip(): continue
        d = json.loads(line)
        if str(d.get("question_id")) == qid:
            (tdir / "files").mkdir(exist_ok=True)
            tests = {k: d.get(k) for k in ("public_test_cases", "private_test_cases", "metadata") if k in d}
            (tdir / "files" / "tests.json").write_text(json.dumps(tests))
            return {"type": "prompt", "prompt": d.get("question_content", ""),
                    "title": d.get("question_title"), "difficulty": d.get("difficulty"),
                    "starter_code": d.get("starter_code", ""), "platform": d.get("platform"),
                    "reference": "run tests.json via LCB evaluator"}
    raise ValueError(f"LCB question_id {qid} not found in test6.jsonl")

def spider2(row, tdir, cache):
    iid = row["source_task_id"]
    blob = _get("https://raw.githubusercontent.com/xlang-ai/Spider2/main/spider2-lite/spider2-lite.jsonl", cache)
    for line in blob.splitlines():
        d = json.loads(line)
        if d.get("instance_id") == iid:
            return {"type": "prompt", "prompt": d.get("question", ""), "db": d.get("db"),
                    "external_knowledge": d.get("external_knowledge"),
                    "reference": "execution-match vs gold SQL result (Spider2-lite eval)"}
    raise ValueError(f"Spider2 {iid} not found")

def cyberseceval(row, tdir, cache):
    idx = int(re.search(r"\[(\d+)\]", row["source_task_id"]).group(1))
    blob = _get_json("https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/datasets/instruct/instruct.json", cache)
    d = blob[idx]
    return {"type": "prompt", "prompt": d.get("test_case_prompt", d.get("mutated_prompt", "")),
            "language": d.get("language"), "cwe": d.get("cwe_identifier"),
            "origin_code": d.get("origin_code", ""), "reference": "Insecure Code Detector + judge"}

def locomo(row, tdir, cache):
    sid = row["source_task_id"]
    blob = _get_json("https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json", cache)
    conv = next(c for c in blob if c.get("sample_id") == sid)
    (tdir / "files").mkdir(exist_ok=True)
    (tdir / "files" / "conversation.json").write_text(json.dumps(conv.get("conversation", {}), ensure_ascii=False))
    qa = conv.get("qa", [])
    return {"type": "prompt", "prompt": "Answer questions about the multi-session conversation in files/conversation.json.",
            "questions": qa, "n_questions": len(qa), "reference": "answer match per LoCoMo eval"}

def eqbench_creative(row, tdir, cache):
    pid = row["source_task_id"]
    blob = _get_json("https://raw.githubusercontent.com/EQ-bench/creative-writing-bench/main/data/creative_writing_prompts_v3.json", cache)
    d = blob[pid]
    prompt = d.get("writing_prompt") or d.get("prompt") or json.dumps(d)
    return {"type": "prompt", "prompt": prompt, "genre": d.get("genre", ""),
            "seed_modifiers": d.get("seed_modifiers", [])[:5],
            "reference": "pairwise judge vs BF16 output, position-swapped"}

def eqbench3(row, tdir, cache):
    sid = row["source_task_id"]
    blob = _get("https://raw.githubusercontent.com/EQ-bench/eqbench3/main/data/scenario_prompts.txt", cache)
    # file format: scenarios separated by headers "#### <id>. <title>" or similar; keep raw block
    pat = re.compile(rf"(?ms)^.*?\bScenario\s+{re.escape(sid)}\b.*?$")
    blocks = re.split(r"\n(?=#{2,4}\s)", blob)
    hit = next((b for b in blocks if re.search(rf"(?m)^#+\s*{re.escape(sid)}[.\s]", b) or f"[{sid}]" in b), None)
    if hit is None:
        # fallback: line-scan window
        lines = blob.splitlines(); hit = None
        for i, ln in enumerate(lines):
            if re.match(rf"^\s*{re.escape(sid)}[.\):\s]", ln):
                hit = "\n".join(lines[i:i+60]); break
    if hit is None: raise ValueError(f"EQ3 scenario {sid} not found")
    return {"type": "prompt", "prompt": hit.strip()[:8000], "multi_turn": True,
            "reference": "rubric judge per EQ-Bench 3 protocol"}

def writingbench(row, tdir, cache):
    idx = row["source_task_id"]
    blob = _get("https://raw.githubusercontent.com/X-PLUG/WritingBench/main/benchmark_query/benchmark_all.jsonl", cache)
    for line in blob.splitlines():
        d = json.loads(line)
        if str(d.get("index")) == idx:
            return {"type": "prompt", "prompt": d.get("query", ""), "domain1": d.get("domain1"),
                    "domain2": d.get("domain2"), "lang": d.get("lang"),
                    "checklist": d.get("checklist", []), "reference": "5 instance criteria judge + critic model"}
    raise ValueError(f"WritingBench index {idx} not found")

def wmt24pp(row, tdir, cache):
    doc = row["source_task_id"]
    rows = _ds_rows("google/wmt24pp", "en-de_DE", "train", 0, 998, cache)
    seg = [r for r in rows if r.get("document_id") == doc and not r.get("is_bad_source")]
    if not seg: raise ValueError(f"wmt24pp doc {doc} not found")
    return {"type": "prompt", "prompt": "Translate the document to German (de_DE), preserving style.",
            "source_segments": [s.get("source") for s in seg],
            "reference_segments": [s.get("target") for s in seg],
            "lp": "en-de_DE", "reference": "COMET (doc-level, per-segment aggregate)"}

def tutoreval(row, tdir, cache):
    idx = int(row["source_task_id"].split("-")[1])
    r = _ds_rows_page("princeton-nlp/TutorEval", "default", "train", idx, 1, cache)[0]
    return {"type": "prompt", "prompt": r.get("question", ""), "chapter": (r.get("chapter") or "")[:20000],
            "closed_book": r.get("closed_book"), "domain_": r.get("domain"),
            "key_points": r.get("key_points", ""), "reference": "GPT-judge vs key points"}

def aime2025(row, tdir, cache):
    tid = row["source_task_id"]  # AIME2025-I-01
    part, num = tid.split("-")[1], int(tid.split("-")[2])
    try:
        rows = _ds_rows_page("opencompass/AIME2025", f"AIME2025-{part}", "test", 0, 15, cache)
    except Exception:  # /rows intermittently 500s for this dataset; /first-rows is reliable
        url = f"https://datasets-server.huggingface.co/first-rows?dataset=opencompass%2FAIME2025&config=AIME2025-{part}&split=test"
        rows = [r["row"] for r in _get_json(url, cache)["rows"]]
    r = rows[num - 1]
    return {"type": "prompt", "prompt": r.get("question", ""), "answer": str(r.get("answer", "")),
            "reference": "exact integer answer"}

def gpqa(row, tdir, cache):
    rid = row["source_task_id"]
    blob = _get("https://github.com/idavidrein/gpqa/raw/main/dataset.zip", cache, binary=True)
    zf = zipfile.ZipFile(io.BytesIO(blob))
    name = next(n for n in zf.namelist() if n.endswith("gpqa_diamond.csv"))
    # zip is password-protected as an anti-crawler canary; password is public in the GPQA README
    rdr = csv.DictReader(io.TextIOWrapper(zf.open(name, pwd=b"deserted-untie-orchid"), encoding="utf-8"))
    for r in rdr:
        if r.get("Record ID") == rid:
            return {"type": "prompt", "prompt": r.get("Question", ""),
                    "correct": r.get("Correct Answer", ""),
                    "incorrect": [r.get(f"Incorrect Answer {i}", "") for i in (1, 2, 3)],
                    "subdomain": r.get("Subdomain", ""), "reference": "multiple-choice match"}
    raise ValueError(f"GPQA {rid} not found")

def artifactsbench(row, tdir, cache):
    idx = row["source_task_id"]
    blob = _get("https://raw.githubusercontent.com/Tencent-Hunyuan/ArtifactsBenchmark/main/dataset/artifacts_bench.json", cache)
    for line in blob.splitlines():
        if not line.strip(): continue
        d = json.loads(line)
        if str(d.get("index")) == idx:
            return {"type": "prompt", "prompt": d.get("question", ""), "cls": d.get("class"),
                    "reference": "MLLM judge on rendered artifact (screenshot rubric)"}
    raise ValueError(f"ArtifactsBench index {idx} not found")

# ---------- file-type ----------

def aider(row, tdir, cache):
    ex = row["source_task_id"]  # e.g. cpp/all-your-base
    lang, name = ex.split("/", 1)
    # single tarball fetch (cached) avoids GitHub API rate limits entirely
    blob = _get("https://codeload.github.com/Aider-AI/polyglot-benchmark/tar.gz/refs/heads/main", cache, binary=True)
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz")
    prefix = f"/{lang}/exercises/practice/{name}/"
    files_dir = tdir / "files"; files_dir.mkdir(exist_ok=True)
    found = False
    for m in tf.getmembers():
        if prefix in m.name and m.isfile():
            rel = m.name.split(prefix, 1)[1]
            dst = files_dir / rel; dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(tf.extractfile(m).read()); found = True
    if not found: raise ValueError(f"aider exercise {ex} not found in tarball")
    p = files_dir / ".docs" / "instructions.md"
    instr = p.read_text() if p.exists() else ""
    return {"type": "files", "prompt": instr or f"Complete the {name} exercise ({lang}); make the tests pass.",
            "entry": ex, "reference": "language test suite"}

def spreadsheetbench(row, tdir, cache):
    iid = row["source_task_id"]
    blob = _get("https://github.com/RUCKBReasoning/SpreadsheetBench/raw/main/data/spreadsheetbench_verified_400.tar.gz", cache, binary=True)
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz")
    dataset = json.load(tf.extractfile(next(m for m in tf.getmembers() if m.name.endswith("dataset.json"))))
    d = next(x for x in dataset if str(x.get("id")) == iid)
    files_dir = tdir / "files"; files_dir.mkdir(exist_ok=True)
    pref = None
    for m in tf.getmembers():
        if f"/{iid}/" in m.name and m.isfile():
            rel = m.name.split(f"/{iid}/", 1)[1]
            dst = files_dir / rel; dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(tf.extractfile(m).read()); pref = True
    return {"type": "files", "prompt": d.get("instruction", ""),
            "instruction_type": d.get("instruction_type"), "answer_position": d.get("answer_position"),
            "spreadsheet_files": bool(pref), "reference": "OJ-style: produced sheet vs answer sheet"}

def gdpval(row, tdir, cache):
    t = row["source_task_id"]
    rows = _ds_rows("openai/gdpval", "default", "train", 0, 220, cache)
    d = next(r for r in rows if r.get("task_id") == t)
    return {"type": "files", "prompt": d.get("prompt", ""), "occupation": d.get("occupation"),
            "sector": d.get("sector"), "reference_files": d.get("reference_files", []),
            "reference": "per-task rubric judge (deliverable = text document)"}

# ---------- block-type (Guardrail & Classification) ----------

def _block_range(row):
    m = re.search(r"rows (\d+)-(\d+)", row["source_task_id"])
    return int(m.group(1)), int(m.group(2))

def _block(rows_list, tdir, label_field, prompt_field, ref):
    (tdir / "files").mkdir(exist_ok=True)
    (tdir / "files" / "block.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, default=str) for r in rows_list))
    return {"type": "block", "n_prompts": len(rows_list), "prompt_field": prompt_field,
            "label_field": label_field, "reference": ref,
            "prompt": f"single-token classification block ({len(rows_list)} prompts); measure label flip rate vs BF16"}

def block_toxicchat(row, tdir, cache):
    a, b = _block_range(row)
    rows = _ds_rows("lmsys/toxic-chat", "toxicchat0124", "test", a, b - a + 1, cache)
    return _block(rows, tdir, "toxicity", "user_input", "flip rate on toxicity + jailbreaking labels")

def block_openai_mod(row, tdir, cache):
    a, b = _block_range(row)
    blob = _get("https://github.com/openai/moderation-api-release/raw/main/data/samples-1680.jsonl.gz", cache, binary=True)
    lines = gzip.decompress(blob).decode("utf-8").splitlines()
    rows = [json.loads(l) for l in lines[a:b + 1]]
    return _block(rows, tdir, "moderation categories (S,H,V,...)", "prompt", "flip rate on category labels")

def block_aegis(row, tdir, cache):
    a, b = _block_range(row)
    rows = _ds_rows("nvidia/Aegis-AI-Content-Safety-Dataset-2.0", "default", "test", a, b - a + 1, cache)
    return _block(rows, tdir, "prompt_label / violated_categories", "prompt", "flip rate on safe/unsafe + categories")

def block_clinc(row, tdir, cache):
    a, b = _block_range(row)
    rows = _ds_rows("clinc/clinc_oos", "plus", "test", a, b - a + 1, cache)
    return _block(rows, tdir, "intent (150 + oos)", "text", "flip rate on intent label")

def block_rewardbench(row, tdir, cache):
    a, b = _block_range(row)
    rows = _ds_rows("allenai/reward-bench", "default", "filtered", a, b - a + 1, cache)
    return _block(rows, tdir, "chosen-vs-rejected verdict", "prompt", "verdict flip rate on preference pairs")
