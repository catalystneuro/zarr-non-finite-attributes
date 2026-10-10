# Non-Finite Attributes Convention

- **UUID**: 2adc9aac-d676-4e93-8feb-903b6ae9e08a
- **Name**: non-finite-attributes
- **Schema URL**: "https://raw.githubusercontent.com/catalystneuro/zarr-non-finite-attributes/refs/tags/v1/schema.json"
- **Spec URL**: "https://github.com/catalystneuro/zarr-non-finite-attributes/blob/v1/README.md"
- **Scope**: Array, Group
- **Extension Maturity Classification**: Proposal
- **Owner**: @bendichter

## Description

This convention defines how the numbers NaN, positive infinity and negative infinity are written in the `attributes` of a Zarr v3 array or group. They are written as the strings `"NaN"`, `"Infinity"` and `"-Infinity"`, which are the forms the Zarr specification already defines for [fill values](https://zarr-specs.readthedocs.io/en/latest/v3/data-types/index.html#permitted-fill-values). A string that has the same characters as one of these is written with the prefix `_str_`, so that every value can be read back as it was written.

The convention follows the [Zarr Conventions Specification](https://github.com/zarr-conventions/zarr-conventions-spec). Unlike most conventions, it does not define a set of attributes. It defines how the values of a node's attributes are encoded, and so it has no properties of its own and no namespace.

- Examples:
  - [Convention metadata only](examples/minimal.json)
  - [An array with non-finite attributes](examples/array.json)
  - [A group with nested values and escaped strings](examples/group_with_escaped_strings.json)

## Motivation

Zarr metadata is JSON as defined by RFC 8259, which has no representation for a number that is not finite. The Zarr specification gives `fill_value` a rule for this and leaves `attributes` to the user. Implementations have each handled a non-finite attribute in their own way:

| What is written for a NaN attribute | Implementations                        |
| ----------------------------------- | -------------------------------------- |
| The bare token `NaN`                | zarr-python, xarray, GDAL, hdmf-zarr   |
| The string `"NaN"`                  | zarrita.js, zarr-java, JZarr, netCDF-C |
| `null`, with the value lost         | zarrs, tensorstore, zarr.js, z5        |
| An error                            | n5-zarr                                |

The bare token is not valid JSON, and most implementations outside Python cannot open a group or array whose attributes hold one. The string is valid and loses nothing on disk, but without a rule a reader cannot tell the number from a string with the same characters. [SURVEY.md](SURVEY.md) has the details, with versions and sources.

This convention gives writers one encoding to agree on:

- **Valid JSON**: every implementation can open the node, whether or not it knows the convention.
- **Reversible**: every number and every string is read back as it was written, including strings that look like the reserved forms.
- **Familiar**: the three strings are the ones the specification uses for fill values, and the ones several implementations already write.
- **Explicit**: only a node that registers the convention is decoded, so the meaning of existing data does not change.

## Convention Registration

The convention must be registered in `zarr_conventions` on every array or group whose attributes are encoded with it:

```json
{
  "zarr_conventions": [
    {
      "schema_url": "https://raw.githubusercontent.com/catalystneuro/zarr-non-finite-attributes/refs/tags/v1/schema.json",
      "spec_url": "https://github.com/catalystneuro/zarr-non-finite-attributes/blob/v1/README.md",
      "uuid": "2adc9aac-d676-4e93-8feb-903b6ae9e08a",
      "name": "non-finite-attributes",
      "description": "Non-finite numbers in attributes are written as strings"
    }
  ]
}
```

Registration applies to the node that holds it. It does not extend to the members of a group, so each node that needs the convention registers it.

## Applicable To

This convention can be used with these parts of the Zarr hierarchy:

- [x] Group
- [x] Array

## Encoding

The three _reserved strings_ are `NaN`, `Infinity` and `-Infinity`. An _affected string_ is a string that consists of zero or more repetitions of the prefix `_str_` followed by exactly one reserved string. The comparison is case sensitive, and no other characters, including whitespace, may be present. Every other string is unaffected.

When writing the attributes of a node that registers the convention, an implementation MUST apply these rules to every value:

1. A number that is not finite is written as the corresponding reserved string.
2. An affected string is written with one additional `_str_` prefix.
3. Any other value is written unchanged.

When reading the attributes of a node that registers the convention, an implementation MUST apply the inverse rules to every value:

1. A string that is exactly a reserved string is read as the corresponding number.
2. An affected string that has one or more `_str_` prefixes is read as a string, with one prefix removed.
3. Any other value is read unchanged.

An affected string therefore always gains exactly one prefix when it is written and loses exactly one when it is read, however many it already has.

| Attribute value                    | Written in `zarr.json`       |
| ---------------------------------- | ---------------------------- |
| the number NaN                     | `"NaN"`                      |
| the number positive infinity       | `"Infinity"`                 |
| the number negative infinity       | `"-Infinity"`                |
| the string `NaN`                   | `"_str_NaN"`                 |
| the string `_str_NaN`              | `"_str__str_NaN"`            |
| the string `_str__str_NaN`         | `"_str__str__str_NaN"`       |
| the string `_str_hello`            | `"_str_hello"`               |
| the strings `nan`, `inf` and `N/A` | `"nan"`, `"inf"` and `"N/A"` |

### Which Values the Rules Apply To

The rules apply to every value within `attributes`, including the members of objects and the elements of arrays at any depth, with these exceptions:

- The value of `zarr_conventions` is written and read as it is.
- The names of the members of an object are never changed.

The rules do not apply to any other part of `zarr.json`. In particular, `fill_value` keeps the encoding the Zarr specification gives it.

### Use with Other Conventions

When a node registers this convention together with others, a reader decodes the attributes with this convention first, and the other conventions are applied to the decoded values. A writer encodes last.

### Bare Tokens

A writer following this convention MUST NOT write the bare tokens `NaN`, `Infinity` or `-Infinity`, which are not valid JSON. A reader MAY accept them as the corresponding numbers, since some implementations have written them.

## Reference Implementations and Test Vectors

The rules are about twenty lines of code in most languages. This repository has reference implementations in [Python](reference/non_finite_attributes.py) and [JavaScript](reference/non_finite_attributes.js), and [test_vectors.json](test_vectors.json) lists values with their encodings for checking other implementations. Both reference implementations are tested against the vectors and the examples.

```bash
npm install
```

```bash
npm test
```

```bash
python reference/test_reference.py
```

## Limitations

- **A reader that does not know the convention gets strings.** The node opens and the other attributes are unaffected, but `"NaN"` is returned as a string. In Python `float("NaN")`, and in JavaScript `Number("NaN")`, convert it.
- **The sign and payload of a NaN are not kept.** An attribute holds a JSON number, which has no data type. The `"0xYYYYYYYY"` form that fill values allow is not a reserved string and is read as a string.
- **Registration is repeated on each node.** A hierarchy with many nodes that hold non-finite attributes carries the convention metadata object on each of them.
- **Existing data is not covered.** A node that does not register the convention is read as it always was, so data written with the string `"NaN"` and no registration stays ambiguous.

## Related Work

- The [fill value encoding](https://zarr-specs.readthedocs.io/en/latest/v3/data-types/index.html#permitted-fill-values) of the Zarr v3 specification uses the same three strings, where the data type of the array says that they denote numbers.
- The [missing_value convention](https://github.com/zarr-conventions/missing_value) reuses the fill value encoding for one attribute of an array.
- [zarr-specs#141](https://github.com/zarr-developers/zarr-specs/issues/141) is the earlier discussion of non-finite numbers in attributes, and [zarr-specs#398](https://github.com/zarr-developers/zarr-specs/pull/398) proposed this encoding for the core specification, where the suggestion was to define it as a convention.
- The JSON mapping of Protocol Buffers writes non-finite doubles as the same three strings.

## Known Implementations

### Libraries and Tools

None yet, apart from the reference implementations in this repository.

_If you implement or use this convention, please add your implementation to this list by submitting a pull request._

## Acknowledgements

This convention uses the [Zarr conventions template](https://github.com/zarr-conventions/template), which is based on the [STAC extensions template](https://github.com/stac-extensions/template/blob/main/README.md).
