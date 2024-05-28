# Contributing guidelines

## Filing issues

File issues using the standard Github issue tracker for the repo.

## How to become a contributor and submit your own code

* Fork the repo and create a dedicated branch.
* Install pre-commit.
* Install the dev dependencies.

The code relies on Ruff for formatting and linting, please have a look at the ruff.toml file.

There are no tests for now, as it is quite difficult to build suitable test suite for CLI. Unit tests should be added in the future.

The repo on GitHub uses GitHub Actions to automate linting/formatting and publishing.

### Contributing A Patch

* Submit an issue describing your proposed change to the repo in question.
* The repo owner will respond to your issue promptly.
* If your proposed change is accepted, and you haven't already done so, sign a Contributor License Agreement (see details above).
* Fork the desired repo, develop and test your code changes.
* Submit a pull request.
