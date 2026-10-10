#!/usr/bin/env node
// Check the JavaScript reference implementation against the shared test vectors.
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import {
  decode,
  decodeAttributes,
  encode,
  encodeAttributes,
} from "./non_finite_attributes.js";

const root = new URL("../", import.meta.url);
const { cases } = JSON.parse(
  readFileSync(new URL("test_vectors.json", root), "utf8"),
);

for (const testCase of cases) {
  const decoded =
    "number" in testCase.decoded
      ? Number(testCase.decoded.number)
      : testCase.decoded.value;
  // deepStrictEqual treats NaN as equal to NaN
  assert.deepStrictEqual(encode(decoded), testCase.encoded);
  assert.deepStrictEqual(decode(testCase.encoded), decoded);
}

for (const file of readdirSync(new URL("examples/", root))) {
  const { attributes } = JSON.parse(
    readFileSync(new URL(`examples/${file}`, root), "utf8"),
  );
  const decoded = decodeAttributes(attributes);
  assert.deepStrictEqual(encodeAttributes(decoded), attributes);
  // What is written is strict JSON
  JSON.parse(JSON.stringify(encodeAttributes(decoded)));
}

assert.deepStrictEqual(decodeAttributes({ resolution: "NaN" }), {
  resolution: "NaN",
});
console.log(`${cases.length} test vectors and the examples pass`);
