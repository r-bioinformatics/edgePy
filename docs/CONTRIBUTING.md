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
    dead_arg: Optional[Any]=None
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

## Running the tests

Make sure to have all test dependencies installed by installing the `ci` requirement group _e.g._:

```bash
❯ pip install -e 'edgePy[ci]'
```

Run the tests with the following command:

```bash
❯ cd edgePy
❯ ./tests/test-runner.sh
❯ ./tests/mypy.sh
```


