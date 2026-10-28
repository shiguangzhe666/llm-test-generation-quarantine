"""
LLM Test Generator using Ollama local models.

Generates pytest unit tests for Python source code using local LLM via Ollama API.

Usage:
    python generate_tests.py --source <file.py> --model qwen3:8b --output <test_file.py>
"""

import json
import sys
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


OLLAMA_API = "http://localhost:11434/api/generate"


def call_ollama(model: str, prompt: str, temperature: float = 0.7) -> str:
    """Call Ollama API and return generated text."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 4096,
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(
        OLLAMA_API,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "")
    except urllib.error.URLError as e:
        print("ERROR: Cannot connect to Ollama at {}".format(OLLAMA_API))
        print("  Make sure Ollama is running: ollama serve")
        print("  Error: {}".format(e))
        sys.exit(1)


BASIC_TEMPLATE = """You are a Python testing expert. Generate pytest unit tests for the following Python code.

## Requirements
- Write thorough pytest test functions
- Include edge cases, boundary conditions, and error handling
- Use descriptive test function names
- Each test should have clear, specific assertions (not just assertNotNone)
- Do NOT use any external services or network calls
- Do NOT use sleep() or time-dependent assertions

## Code Under Test

File: {filepath}

```python
{source}
```

## Output

Write ONLY the Python test code. Start with necessary imports. Do NOT include any explanation or markdown formatting.
"""


UNCONSTRAINED_TEMPLATE = """Generate comprehensive pytest unit tests for this Python code.
Test all functions thoroughly including edge cases.

```python
{source}
```

Write ONLY the Python test code, starting with imports. No explanations.
"""


def extract_code_from_response(response: str) -> str:
    """Extract Python code from LLM response, stripping think tags and markdown fences.
    
    Handles:
    - qwen3's <think>...</think> reasoning blocks
    - Markdown ```python ... ``` code fences (single or multiple blocks)
    - Leading non-code text (explanations, comments about the code)
    """
    import re as _re
    
    text = response.strip()
    
    # Step 1: Remove <think>...</think> blocks (qwen3 reasoning)
    text = _re.sub(r"<think>.*?</think>", "", text, flags=_re.DOTALL).strip()
    
    # Step 2: Extract code from markdown fenced blocks if present
    code_blocks = _re.findall(
        r"```(?:python|py)?\s*\n(.*?)```",
        text,
        flags=_re.DOTALL,
    )
    
    if code_blocks:
        # Concatenate all code blocks
        text = "\n\n".join(block.strip() for block in code_blocks)
    else:
        # No markdown fences — try to strip any remaining fences
        lines = text.split("\n")
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    
    # Step 3: Remove any leading non-code text
    lines = text.split("\n")
    code_started = False
    code_lines = []
    for line in lines:
        if not code_started:
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "#", "def ", "class ",
                                    '"""', "'''", "@", "pytest")):
                code_started = True
                code_lines.append(line)
        else:
            # Stop if we hit another think block or markdown fence
            if line.strip().startswith(("<think>", "```")):
                break
            code_lines.append(line)
    
    return "\n".join(code_lines) if code_lines else text


def generate_tests(
    source_code: str,
    filepath: str = "module.py",
    model: str = "qwen3:8b",
    template: str = "basic",
    temperature: float = 0.7,
) -> dict:
    """Generate tests for given source code."""
    
    if template == "basic":
        prompt = BASIC_TEMPLATE.format(filepath=filepath, source=source_code)
    else:
        prompt = UNCONSTRAINED_TEMPLATE.format(source=source_code)
    
    print("Generating tests with {} (temp={})...".format(model, temperature))
    start = datetime.now()
    
    raw_response = call_ollama(model, prompt, temperature)
    
    duration = (datetime.now() - start).total_seconds()
    print("  Generated in {:.1f}s ({} chars)".format(duration, len(raw_response)))
    
    test_code = extract_code_from_response(raw_response)
    
    return {
        "model": model,
        "template": template,
        "temperature": temperature,
        "source_file": filepath,
        "generation_time_seconds": round(duration, 2),
        "raw_response_length": len(raw_response),
        "test_code_length": len(test_code),
        "test_code": test_code,
        "raw_response": raw_response,
        "timestamp": datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate pytest tests using local Ollama LLM")
    parser.add_argument("--source", required=True, help="Path to Python source file")
    parser.add_argument("--model", default="qwen3:8b", help="Ollama model name")
    parser.add_argument("--output", default=None, help="Output test file path")
    parser.add_argument("--template", choices=["basic", "unconstrained"], default="basic")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--runs", type=int, default=1, help="Number of generation runs")
    args = parser.parse_args()
    
    source_path = Path(args.source)
    if not source_path.exists():
        print("ERROR: Source file not found: {}".format(source_path))
        sys.exit(1)
    
    source_code = source_path.read_text(encoding="utf-8")
    print("Source: {} ({} lines)".format(source_path, len(source_code.split(chr(10)))))
    
    results = []
    for i in range(args.runs):
        if args.runs > 1:
            print("\n--- Run {}/{} ---".format(i + 1, args.runs))
        
        result = generate_tests(
            source_code=source_code,
            filepath=str(source_path),
            model=args.model,
            template=args.template,
            temperature=args.temperature,
        )
        results.append(result)
        
        # Save test code
        if args.output:
            if args.runs == 1:
                out_path = Path(args.output)
            else:
                stem = Path(args.output).stem
                suffix = Path(args.output).suffix
                out_path = Path(args.output).parent / "{}_{:02d}{}".format(stem, i, suffix)
            
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(result["test_code"], encoding="utf-8")
            print("  Saved: {}".format(out_path))
    
    # Save metadata
    meta_path = Path(args.output or "test_generated.py").with_suffix(".meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        # Don't save raw_response in meta to keep it small
        meta = [{k: v for k, v in r.items() if k != "raw_response"} for r in results]
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print("\nMetadata saved: {}".format(meta_path))


if __name__ == "__main__":
    main()
