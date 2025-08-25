# JSON
import json
import warnings
from json import JSONDecoder, JSONDecodeError
from typing import Any, List, Sequence

import re

# ════════════════════════════════════════════════════════════════════
# String Format helper
# ════════════════════════════════════════════════════════════════════
def get_first_json(s: str) -> Any:
    """
    Scan *s* left‑to‑right and return the first full JSON object.

    If a later opening brace is never matched with a closing brace
    (i.e. an unfinished JSON fragment), emit a RuntimeWarning.

    Raises
    ------
    ValueError
        If no valid JSON object is found.
    """
    decoder = JSONDecoder()
    idx = 0

    while True:
        try:
            # Find the next candidate '{'
            start = s.index('{', idx)
        except ValueError:
            raise ValueError("No JSON object found in the supplied string.") from None

        try:
            obj, end = decoder.raw_decode(s, start)
            # ---- Found the first complete JSON object ----
            # Check the remainder for unmatched opening brace(s)
            tail = s[end:]
            if tail.count('{') > tail.count('}'):
                warnings.warn(
                    "Trailing text looks like an incomplete JSON object.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            return obj
        except JSONDecodeError:
            # Not a valid object starting here; move one character forward
            idx = start + 1

def combine_list2str(items: List[str]) -> str:
    """Combine a list of strings into one long string."""
    return "".join(items)




def first_sentence(text: str, *, eos: Sequence[str] = (".", "?", "!")) -> str:
    """
    Return the first sentence in *text*.

    Parameters
    ----------
    text : str
        The input string.
    eos : sequence of str, optional
        Characters that mark sentence endings.  Default: ('.', '?', '!')
        Pass a different set to customize—e.g. eos=("。",) for Japanese.
    """
    if not text:
        return ""

    # Escape each terminator for regex and join into a character class
    eos_class = "[" + re.escape("".join(eos)) + "]"

    # Non‑greedy up to the first terminator followed by space or end‑of‑string
    pattern = rf"(.+?{eos_class})(?:\s|$)"
    match = re.search(pattern, text.strip(), re.DOTALL)

    return match.group(1).strip() if match else text.strip()


import re, json

def single_key_bool_json_fix(text: str, field: str = "is_story") -> dict:
    """
    Extract and normalize JSON from model output.
    Ensures keys are quoted and values for the target field are always strings ("true"/"false").
    For correct input {"is_story":"true"}, this function manages to handle wrong
    jsons such as
    {is_story:"true"}, {is_story:"true"} 
    
    """
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return {}
        candidate = match.group(0)

        # 1. Ensure keys are quoted: {field:...} → {"field":...}
        candidate = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', candidate)

        # 2. Normalize boolean-ish values for the target field into quoted strings
        #    {"field":true} → {"field":"true"}
        #    {"field":false} → {"field":"false"}
        candidate = re.sub(
            rf'"{field}"\s*:\s*true',
            f'"{field}":"true"',
            candidate,
            flags=re.IGNORECASE
        )
        candidate = re.sub(
            rf'"{field}"\s*:\s*false',
            f'"{field}":"false"',
            candidate,
            flags=re.IGNORECASE
        )

        return json.loads(candidate)
    except Exception as e:
        print(f"extract_json error for {field}:", e, text)
        return {}
