# Contributing

When contributing to this repository discuss the change you wish to make _via_ this project's [GitHub issues](https://github.com/r-bioinformatics/edgePy/issues) first.

## PR Process for Project Contributers

Always ensure that you have fetched (_via_ `git pull`) the most recent material into your local clone.

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

1. Strictly adhere to PEP8.
2. Use [Google Style](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstrings.
3. Implement doctests.
4. Provide accurate type annotations.
5. Limit line lengths to 120 characters.

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

### Code Style
This repository uses [Black](https://github.com/ambv/black) as a code formatter.

It can be ran a few different ways:

1. Manually by running `$ black .` in the repository root
2. Though [pre-commit](https://pre-commit.com/) a git hook that runs it whenever a commit is made.
3. It can also be integrated in the of your choice by following the instructions in the [documention](https://github.com/ambv/black#editor-integration).

## Updating the documentation

New documentation files must be of the following format:
- reStructuredText (**.rst**) -- _preferred_
- Markdown (**.md**)

A new file can be added to the appropriate gloassary tree in `edgePy/docs/source/index.rst`.

The service `readthedocs.org` will automatically source the *conf.py* file in `edgePy/docs/sources/conf.py` and update the docs accordingly on each commit pushed to GitHub, on any branch.

Local HTML renders of the documentation can be built with the following:

```bash
❯ cd edgePy/docs
❯ pip install -r requirements-docs.txt
❯ make html
```

This will create or update the HTML documents in the `\docs\_build\html` directory.

## Developing in a Virtual Environment

The development environment is listed as an additional `Tox` environment:

```bash
❯ tox -lv

using tox.ini: .../edgePy/tox.ini
using tox-3.1.2 from .../python3.6/dist-packages/tox/__init__.py
default environments:
py36      -> run the test suite with (basepython)
py36-lint -> check the code style
py36-type -> type check the library
py36-docs -> test building of HTML docs

additional environments:
dev       -> the official edgePy development environment
```

To create and activate that environment issue the following:

```bash
❯ cd edgePy
# Create the development environment (force recreation)
❯ tox --recreate -e dev
# Activate the development environment
❯ source venv/bin/activate

```

## Running the Test Suite

All tests are coordinated by `Tox`. Running the unit tests, code coverage, code style (linting) checks, static analysis of typing, and successful compilation of the docs is as simple as the following commands!

> **Note**: This command takes a long time the first time it is invoked since all virtual environments need to be created!

```bash
❯ cd edgePy
❯ tox
```

## Running Parts of the Test Suite

You can select only a part of the test suite by looking at which `Tox` groups are available:

```bash
❯ cd edgePy
❯ tox -lv

using tox.ini: ../edgePy/tox.ini
using tox-3.1.2 from ../python3.6/dist-packages/tox/__init__.py
default environments:
py36      -> run the test suite with (basepython)
py36-lint -> check the code style
py36-type -> type check the library
py36-docs -> test building of HTML docs
```

Choose a specific group to run with the following syntax:

```bash
❯ cd edgePy
❯ tox -e py36-type
```

Almost all dynamic and static analysis tools are configured in `setup.cfg` so check there for the configuration of the test suite first.
