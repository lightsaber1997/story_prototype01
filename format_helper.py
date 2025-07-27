# JSON
import json
import warnings
from json import JSONDecoder, JSONDecodeError
from typing import Any

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