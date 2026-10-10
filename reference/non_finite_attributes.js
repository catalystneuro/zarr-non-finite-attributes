// Reference implementation of the Non-Finite Attributes convention in JavaScript.

export const UUID = "2adc9aac-d676-4e93-8feb-903b6ae9e08a";
const AFFECTED = /^(?:_str_)*(?:NaN|Infinity|-Infinity)$/;
const PREFIX = "_str_";

/** Return value as it is written in zarr.json. */
export function encode(value) {
  if (typeof value === "number" && !Number.isFinite(value)) {
    return Number.isNaN(value) ? "NaN" : value > 0 ? "Infinity" : "-Infinity";
  }
  if (typeof value === "string") {
    return AFFECTED.test(value) ? PREFIX + value : value;
  }
  if (Array.isArray(value)) {
    return value.map(encode);
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, encode(item)]),
    );
  }
  return value;
}

/** Return the value that an entry of zarr.json stands for. */
export function decode(value) {
  if (typeof value === "string" && AFFECTED.test(value)) {
    return value.startsWith(PREFIX)
      ? value.slice(PREFIX.length)
      : Number(value);
  }
  if (Array.isArray(value)) {
    return value.map(decode);
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, decode(item)]),
    );
  }
  return value;
}

/** Whether a node's attributes register the convention. */
export function declares(attributes) {
  const conventions = attributes.zarr_conventions ?? [];
  return conventions.some((entry) => entry?.uuid === UUID);
}

/** Encode every attribute of a node except zarr_conventions, which is written as it is. */
export function encodeAttributes(attributes) {
  return Object.fromEntries(
    Object.entries(attributes).map(([key, value]) => [
      key,
      key === "zarr_conventions" ? value : encode(value),
    ]),
  );
}

/** Decode every attribute of a node that registers the convention; return any other node's unchanged. */
export function decodeAttributes(attributes) {
  if (!declares(attributes)) {
    return attributes;
  }
  return Object.fromEntries(
    Object.entries(attributes).map(([key, value]) => [
      key,
      key === "zarr_conventions" ? value : decode(value),
    ]),
  );
}
