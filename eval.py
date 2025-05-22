import json
import asyncio
from openai import OpenAI, AsyncOpenAI
import os

from tabulate import tabulate  # pip install tabulate

api_key = "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"

def build_prompt(chunk):
    """
    Given a list of records (each with 'target' and '<answer>(X)<answer>), construct
    a prompt asking the model to evaluate correctness for each.
    """
    examples = "\n".join(json.dumps(rec) for rec in chunk)
    return (
        "You are given exactly 10 JSON records,\n"
        "each with fields 'target' and 'Final Answer'.\n"
        "Return a JSON array of 10 objects, each containing:\n"
        "  - target\n"
        "  - answer\n"
        "  - correct (true/false)\n\n"
        f"Here are the records:\n{examples}\n"
    )

async def evaluate_chunk(semaphore: asyncio.Semaphore, chunk: list, model: str):
    async with semaphore:
        prompt = build_prompt(chunk)
        resp = await AsyncOpenAI(api_key=api_key).chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        # 1) grab the raw text
        raw = resp.choices[0].message.content
        # 2) strip whitespace and common fences
        raw = raw.strip()
        # remove ```json or ``` fences if present
        if raw.startswith("```"):
            # drop leading and trailing ``` blocks
            raw = raw.strip("```")
        # 3) extract the first JSON array [...]
        import re
        match = re.search(r"\[.*\]", raw, re.S)
        if not match:
            # no array found — show you what we got
            raise ValueError(f"Could not find JSON array in:\n{raw}")
        array_text = match.group(0)
        # 4) parse it
        return json.loads(array_text)

async def evaluate_jsonl(path: str, model: str = "o4-mini"):
    # 1) load all records
    with open(path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    # 2) split into chunks of 10
    chunks = [records[i:i+10] for i in range(0, len(records), 10)]
    # 3) parallelize up to 10 chunks at once (100 records)
    sem = asyncio.Semaphore(10)
    tasks = [evaluate_chunk(sem, chunk, model) for chunk in chunks]
    all_results = await asyncio.gather(*tasks)
    # 4) flatten
    flat = [r for chunk in all_results for r in chunk]

    # 5) tabulate and compute accuracy
    rows = []
    correct_count = 0
    for idx, rec in enumerate(flat, 1):
        is_correct = rec.get("correct", False)
        if is_correct:
            correct_count += 1
        rows.append([
            idx,
            rec.get("target"),
            rec.get("answer"),
            "✓" if is_correct else "✗"
        ])

    table_str = tabulate(rows, headers=["#", "Target", "Final Answer", "Correct"], tablefmt="github")

    # Save to a file
    with open("bbh4_table.txt", "w", encoding="utf-8") as f:
        f.write(table_str)
    accuracy = correct_count / len(flat) * 100
    print(f"\nOverall accuracy: {correct_count}/{len(flat)} = {accuracy:.1f}%")

if __name__ == "__main__":
    import sys
    path = "results/BBH/new_results4.jsonl"
    # path = "results/math/results2.jsonl"
    # path = "results/LongBench/results3.jsonl"
    path = "results/MMLU-CF/new_results4.jsonl"
    # path = "results/HotpotQA/results3.jsonl"
    asyncio.run(evaluate_jsonl(path))
