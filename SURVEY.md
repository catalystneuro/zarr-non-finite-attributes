# What Implementations Do with Non-Finite Attributes

This is a survey, made in October 2026, of what Zarr implementations write when an attribute is NaN or infinite and what they do when they read one. Rows marked "tested" were run with the version given. Rows marked "source" come from reading the implementation's source and were not run.

## Python and C Libraries

| Library                                        | Basis  | Writes for NaN                                     | Reads bare `NaN`               | Reads the string `"NaN"` as                                         |
| ---------------------------------------------- | ------ | -------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------- |
| zarr-python 3.4.1 (formats 2 and 3) and 2.18.7 | tested | bare `NaN`                                         | yes, as a float                | a string                                                            |
| xarray 2026.9.0 with zarr 3.4.1                | tested | bare `NaN`, with no special handling of attributes | yes                            | a string                                                            |
| GDAL 3.12.2 Zarr driver                        | tested | bare `NaN`; the fill value is `"NaN"`              | yes, as Float64                | a string attribute                                                  |
| netCDF-C 4.9.3 (NCZarr, format 2)              | tested | the strings `"NaN"`, `"Infinity"`, `"-Infinity"`   | yes                            | a float when its own type annotation is present, otherwise a string |
| tensorstore 0.1.84, `zarr3` driver             | tested | `null`                                             | no, the array cannot be opened | a string                                                            |
| hdmf-zarr 0.14.0                               | tested | bare `NaN`                                         | yes                            | fails with a type error                                             |
| kerchunk 0.2.10                                | tested | passes bare tokens through unchanged               | passes through                 | passes through                                                      |
| Icechunk 2.3.0                                 | tested | stores the bytes it is given                       | no, refuses the metadata       | passes through                                                      |

JSON libraries for Python, all tested: `json` (CPython 3.12) and `ujson` 6.0.0 write and read the bare tokens. `orjson` 3.13.0 and `msgspec` 0.22.0 write `null` and reject the bare tokens. `simplejson` 4.2.0 raises on writing and rejects the bare tokens.

## Other Implementations

| Implementation             | Basis  | JSON library                                       | Writes for NaN     | Reads bare `NaN`                      |
| -------------------------- | ------ | -------------------------------------------------- | ------------------ | ------------------------------------- |
| zarrita.js 0.7.5           | tested | `JSON.parse`, and `JSON.stringify` with a replacer | the string `"NaN"` | no                                    |
| zarr.js 0.6.3              | source | `JSON.parse` and `JSON.stringify`                  | `null`             | no                                    |
| zarrs                      | source | serde_json                                         | `null`             | no                                    |
| zarr-java                  | source | Jackson with default settings                      | the string `"NaN"` | no                                    |
| JZarr                      | source | Jackson with default settings                      | the string `"NaN"` | no                                    |
| netcdf-java (reading only) | source | Jackson with default settings                      | not applicable     | no                                    |
| n5-zarr                    | source | Gson                                               | raises an error    | yes, as a string that converts to NaN |
| Neuroglancer               | source | the browser's `response.json()`                    | not applicable     | no                                    |
| z5                         | source | nlohmann::json                                     | `null`             | no                                    |

Zarr.jl depends on the major version of JSON.jl that is installed. From its source, it writes `null` with the older version and raises with the newer one, and it rewrites some bare `NaN` tokens as strings before parsing.

## Observations

- No reader converts the string `"NaN"` in an attribute to a number, apart from netCDF-C with its own type annotations.
- zarrita.js writes the attributes `{"a": NaN, "d": "NaN"}` as `{"a": "NaN", "d": "NaN"}`, which shows why the string alone is ambiguous.
- `null` is not a workable substitute. It loses the value, and of the readers tested, hdmf rejects it, netCDF-C returns the text `null`, and GDAL returns an empty string.
