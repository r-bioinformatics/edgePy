# Contributing

When contributing to this repository discuss the change you wish to make _via_ this project's [GitHub issues](https://github.com/r-bioinformatics/edgePy/issues) first.

## PR Process for Project Contributers

Always ensure that you have fetched the most recent material into your local clone.

1. Checkout a branch (`git checkout -b <branch_name>`) prefixed with your initials and suffixed with the issue you are addressing or a brief few words describing the feature/bug fix joined by underscores (`_`). Here are valid formats:
    - `cv_issue_45`
    - `af_issue_2123`
    - `cv_fix_requests_regression`
    - `af_transpose_docs`
2. Commit changes.
3. Execute and create tests regularly. Use `py.test`.
4. Request informal review from peers by pointing them to your branch.
5. Create a Pull Request against `master` when a formal review is needed.
6. Optionally, squash commits and reword messages as needed for easier review.
7. Ensure all continuous integration (CI) tests and code reviews pass before rebasing (or squashing and then rebasing) onto `master`.

    - Avoid directly merging a PR onto `master` without first rebasing.

## Documentation and Code Style

1. Strictly adhere to PEP8. Code will not be linted although all reviewers will check for style adherence.
2. Use [Google Style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstrings.
3. Implement doctests.
4. Provide accurate type annotations.
5. Limit line lengths to 100 columns.

An example function showcasing the above requirements:

```python
def get_dataset_path(
    filename: Union[str, Path],
    dead_arg: Optional[Any] = None
) -> Path:
    """Example function with PEP 484 type annotations.

    Args:
        filename: The first parameter.
        dead_arg: The second parameter.

    Returns:
        The path to the dataset, may not really exist.

    Examples:
        >>> from module.io import get_dataset_path
        >>> str(get_dataset_path("GSE49712_HTSeq.txt.gz"))  # doctest:+ELLIPSIS
        '.../data/GSE49712_HTSeq.txt.gz'

    Notes:
        1. See ``module.rationalize`` for an equivalent method.

    """
    import module
    directory = Path(module.__file__).expanduser().resolve().parent
    return directory / 'data' / filename
```

## Installing as an Editable Package

You will need both documentaiton building and testing dependencies installed.
These dependencies exist in the `ci` and `docs` requirement groups:

```bash
❯ pip install --editable 'edgePy[ci,docs]'
```

## Running the tests

Run the tests with the following command:

```bash
❯ cd edgePy
❯ ./tests/test-runner.sh  # Run all doc and unit tests
❯ ./tests/flake8.sh       # Check for PEP8 style adherence
❯ ./tests/pylint.sh       # Stricter style and logic checking
❯ ./tests/mypy.sh         # Statically check optional type annotations
```

## Updating the documentation

If you created a new documentation file, make sure that it is in markdown (**.md**) or reStructuredText (**.rst**) formats, preferably the latter. The new file should also be located under `\docs`.

Add the name of the new documentation file under the appropriate tree in `\docs\index.rst`.

At this point, you are done adding to the documentation. readthedocs.org will automatically run the *conf.py* file and update the docs accordingly on each commit. 

Optionally for local testing, you can build local HTML files of the documentation as follows:

Build the documentation in HTML format with:

```bash
❯ cd docs
❯ make html
```

In a windows environment, you need to have `MinGW` installed to run the make command, and you may have to switch to the `cmd` terminal.

The make operation should update the html documents in the `\docs\_build\html` directory.
