# BLAST Sandbox - Bit Academy

Execute BLAST tests locally for education development. Currently supporting
PHP tests with PHPUnit, NodeJS tests with Jasmine, Python and Jupyter Notebook (Python) tests with unittest.

## Requirements

> Python 3.10+
> PHP 8.1+
> Composer 2.2+
> Node.js v18+

## Installation

```shell
CLONE THE REPOSITORY <-- Veranderen naar GITLABLINK @BOB
cd blast-sandbox
composer install
npm install
```

## PHP / JavaScript Usage

Write your PHP tests in `tests/php/BLASTTest.php`. Any files used by the
tests can be placed in `tests/php/source_dir`. The same goes for JavaScript,
except the tests are written in `tests/javascript/blastSpec.js` and source
files go into `tests/javascript/source_dir`. To execute PHP tests, use
command `composer run test`. To execute Node tests, use command `npm run test`.

There is one test file for each language. You are expected to write your
tests in this file, make sure they work correctly, and then move the test
source code over to Notion.

## Python / Jupyter Notebook Usage

### Python tests

- Write the test in `python-test.py`
- Place the python file to be tested in the `src` folder
- Run the test with `python python-test.py`

> NOTE: Python files using external imports (outside of standard library) can't be run by BLAST

#### Example test

```python
import unittest
import testUtils

class TestStudentCode(unittest.TestCase):

    # @message: Tests of de output hello world is
    def test_OutputIsHelloWorld(self):
        output = testUtils.run_student_file("hello_world.py") # Looks in `src` folder for this file
        self.assertRegex(output, "hello world!")


if __name__ == '__main__':
    unittest.main()
```

### Jupyter tests

_Currently: **only linting is supported** for Jupyter Notebooks_

- Write the test in `jupyter-test.py`
- Place the Jupyter Notebook to be tested in the `src` folder
- Run the test with `python jupyter-test.py`

#### Example test 2

```python
import unittest
import testUtils

@testUtils.lint_jupyter_notebook(f"notebook.ipynb") # looks in `src` folder for this file
class TestStudentCode(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()

```

## Notes

- In `testUtils.py` there are some useful helper-functions for testing.
- Don't know how to write a test? The Python unittest documentation is the place to be.
