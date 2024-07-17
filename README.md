# Object Filtering

A Python module that functions for determining whether arbitrary Python objects meet a set of defined criteria. Filters use JSON to represent a set of criteria that objects must meet. Filters can be arbitrarily nested and can contain conditional logic.

See `/docs/filter_specifications.md` for details on filter implementation.

## Installation Options

1. Download the latest version of `object_filtering` from PyPi by running the command `pip install object_filtering`.
2. Download the latest version of `object_filtering` from the Releases tab on GitHub and install the wheel (`.whl`).

## Making Modifications

1. Clone this repository.
2. Make modifications to the source code.
3. (Optional) Change the module version in `pyproject.toml`.
4. Run `pytest` from the root of the repository to run unit tests. Only continue if all tests pass.
5. Build the module by running `py -m build` from the root of the repository.
6. Install the newly built wheel file.

## License

(c) 2024 Scott Ratchford.

`object_filtering` is licensed under the MIT License. See `LICENSE.txt` for details.
