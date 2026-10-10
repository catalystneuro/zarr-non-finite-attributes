"""Check the Python reference implementation against the shared test vectors."""

import json
import math
import pathlib
import random

from non_finite_attributes import decode, decode_attributes, encode, encode_attributes

ROOT = pathlib.Path(__file__).resolve().parent.parent


def same(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return (math.isnan(a) and math.isnan(b)) or a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[key], b[key]) for key in a)
    return a == b


def main():
    cases = json.loads((ROOT / "test_vectors.json").read_text())["cases"]
    for case in cases:
        decoded = float(case["decoded"]["number"]) if "number" in case["decoded"] else case["decoded"]["value"]
        assert same(encode(decoded), case["encoded"]), case
        assert same(decode(case["encoded"]), decoded), case

    # Random nested values survive a round trip through a strict JSON encoder
    rng = random.Random(0)
    pieces = ["_str_", "NaN", "Infinity", "-Infinity", "nan", "_", "str", " ", "x", "-", "_STR_"]
    scalars = [float("nan"), float("inf"), float("-inf"), 1.5, 0, None, True, "", "hello"]

    def value(depth=0):
        r = rng.random()
        if depth < 3 and r < 0.15:
            return [value(depth + 1) for _ in range(rng.randrange(4))]
        if depth < 3 and r < 0.3:
            return {"".join(rng.choices(pieces, k=rng.randrange(1, 4))): value(depth + 1) for _ in range(rng.randrange(4))}
        if r < 0.6:
            return rng.choice(scalars)
        return "".join(rng.choices(pieces, k=rng.randrange(0, 5)))

    for _ in range(50_000):
        v = value()
        text = json.dumps(encode(v), allow_nan=False)
        assert same(decode(json.loads(text)), v), v

    # The examples decode, and encode back to what the files hold
    for path in sorted((ROOT / "examples").glob("*.json")):
        attributes = json.loads(path.read_text())["attributes"]
        decoded = decode_attributes(attributes)
        assert same(encode_attributes(decoded), attributes), path.name

    # A node that does not register the convention is left alone
    assert decode_attributes({"resolution": "NaN"}) == {"resolution": "NaN"}
    print(f"{len(cases)} test vectors, 50000 random values, and the examples pass")


if __name__ == "__main__":
    main()
