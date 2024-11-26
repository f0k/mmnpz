# Contributing

Thank you for considering contributing! In the following, we will go through different ways to contribute.

*Acknowledgements:* This page heavily borrows from [Ai2's python package template](https://github.com/allenai/python-package-template).

## Report

When you found a bug or a documentation problem, first do [a quick search](https://github.com/f0k/mmnpz/issues) to see whether your issue has already been reported.  If so, please comment on the existing issue.

Otherwise, open [a new GitHub issue](https://github.com/f0k/mmnpz/issues).  Be sure to include a clear title
and description.  The description should include as much relevant information as possible.  The description should
explain how to reproduce the erroneous behavior as well as the behavior you expect to see.  Ideally you would include a
code sample or an executable test case demonstrating the expected behavior.

## Idea

If you have a suggestion for an enhancement or a new feature, first do [a quick search](https://github.com/f0k/mmnpz/issues) to see whether your idea has already been suggested.
If a similar suggestion already exists, please comment on it.

Otherwise, open [a new GitHub issue](https://github.com/f0k/mmnpz/issues).  Be sure to include a clear title and description.  Explain why the enhancement would be useful.  Include code examples to demonstrate how the enhancement would be used.

## Code

When you're ready to contribute code to address an open issue, please follow these guidelines to help us be able to review your pull request (PR) quickly.

1. **Initial setup** (only do this once)

    <details><summary>Expand details 👇</summary><br/>

    If you haven't already done so, please [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) this repository on GitHub.

    Then clone your fork locally with

        git clone https://github.com/USERNAME/mmnpz.git

    or

        git clone git@github.com:USERNAME/mmnpz.git

    At this point the local clone of your fork only knows that it came from *your* repo, https://github.com/USERNAME/mmnpz.git, but doesn't know the *main* repo, [https://github.com/f0k/mmnpz.git](https://github.com/f0k/mmnpz). You can see this by running

        git remote -v

    which will output something like this:

        origin https://github.com/USERNAME/mmnpz.git (fetch)
        origin https://github.com/USERNAME/mmnpz.git (push)

    This means that your local clone can only track changes from your fork, but not from the main repo, and so you won't be able to keep your fork up-to-date with the main repo over time. Therefore you'll need to add another "remote" to your clone that points to [https://github.com/f0k/mmnpz.git](https://github.com/f0k/mmnpz). To do this, run the following:

        git remote add upstream https://github.com/f0k/mmnpz.git

    Now if you do `git remote -v` again, you'll see

        origin https://github.com/USERNAME/mmnpz.git (fetch)
        origin https://github.com/USERNAME/mmnpz.git (push)
        upstream https://github.com/f0k/mmnpz.git (fetch)
        upstream https://github.com/f0k/mmnpz.git (push)

    Finally, you'll need to create a Python 3 virtual environment suitable for working on this project. There are a number of tools out there that making working with virtual environments easier.
    The most direct way is with the [`venv` module](https://docs.python.org/3.8/library/venv.html) in the standard library, but if you're new to Python or you don't already have a recent Python 3 version installed on your machine,
    you can also use [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

    With venv, you can create and activate a new Python environment in a `.venv` subdirectory by running:

        python3 -m venv .venv
        . .venv/bin/activate

    With Miniconda, you can create and activate a new Python environment by running:

        conda create -n mmnpz python=3.9
        conda activate mmnpz

    Once your virtual environment is activated, you can install your local clone in "editable mode" with

        pip install -U pip setuptools wheel
        pip install -e .[dev]

    The "editable mode" comes from the `-e` argument to `pip`, and essentially just creates a symbolic link from the site-packages directory of your virtual environment to the source code in your local clone. That way any changes you make will be immediately reflected in your virtual environment.

    </details>

2. **Ensure your fork is up-to-date**

    <details><summary>Expand details 👇</summary><br/>

    Once you've added an "upstream" remote pointing to [https://github.com/f0k/mmnpz.git](https://github.com/f0k/mmnpz), keeping your fork up-to-date is easy:

        git pull --rebase upstream/main

    This command will update the current branch to reflect any changes from the main repo. If you run this command from a branch that has local commits, their changes will be replayed on top of the current state of the main repo.

    </details>

3. **Create a new branch to work on your fix or enhancement**

    <details><summary>Expand details 👇</summary><br/>

    Committing directly to the main branch of your fork is not recommended. It will be easier to keep your fork clean if you work on a separate branch for each contribution you intend to make.

    You can create a new branch with

        # replace BRANCH with whatever name you want to give it
        git checkout -b BRANCH
        git push -u origin BRANCH

    </details>

4. **Test your changes**

    <details><summary>Expand details 👇</summary><br/>

    Our continuous integration (CI) testing runs [a number of checks](https://github.com/f0k/mmnpz/actions) for each pull request on [GitHub Actions](https://github.com/features/actions). You can run most of these tests locally, which is something you should do *before* opening a PR to help speed up the review process and make it easier for us.

    First, you should run [`isort`](https://github.com/PyCQA/isort) and [`black`](https://github.com/psf/black) to make sure you code is formatted consistently.
    Many IDEs support code formatters as plugins, so you may be able to setup isort and black to run automatically everytime you save.
    But both `isort` and `black` are also easy to run directly from the command line.
    Just run this from the root of your clone:

        isort .
        black .

    If you have `make` installed, you can also run:

        make format

    Our CI also uses [`ruff`](https://github.com/astral-sh/ruff) to lint the code base and [`mypy`](http://mypy-lang.org/) for type-checking. You should run both of these next with

        ruff check .

    and

        mypy .

    We also maintain 100% test coverage, so contributions may need to include additions to [the unit tests](https://github.com/f0k/mmnpz/tree/main/tests). These tests are run with [`pytest`](https://docs.pytest.org/en/latest/), which you can use to locally run any test modules that you've added or changed:

        pytest -v tests/

    To run all of the above checks, you can use the included `Makefile` and run:

        make tests

    If your contribution involves additions to any public part of the API, we require that you write docstrings
    for each function, method, class, or module that you add.
    See the [Documentation](#documentation) section below for details on the syntax.

    To compile the documentation locally, install the respective requirements with:

        pip install -e .[doc]

    Then test that the API documentation can build without errors by running

        make docs

    If the build fails, it's most likely due to small formatting issues. If the error message isn't clear, feel free to comment on this in your pull request.

    And finally, please update the [CHANGELOG](https://github.com/f0k/mmnpz/blob/main/CHANGELOG.md) with notes on your contribution in the "Unreleased" section at the top.

    After all of the above checks have passed, you can now open [a new GitHub pull request](https://github.com/f0k/mmnpz/pulls).
    Make sure you have a clear description of the problem and the solution, and include a link to relevant issues.

    We look forward to reviewing your PR!

    </details>

## Documentation

Along with your code, but also as an independent contribution, you may want to
update the documentation. We use [Sphinx](https://www.sphinx-doc.org/)
to build our documentation. The main documents are in
[MyST Markdown format](https://myst-parser.readthedocs.io/) in the
[`docs`](https://github.com/f0k/mmnpz/tree/main/docs) directory. Docstrings of
classes and methods are parsed by
[autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html).
As **mmnpz** targets numpy, we use
[numpy's docstring standard](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard).
To test your documentation changes locally, install the requirements with
`pip install -e .[doc]` and build the documentation with `make docs`.
