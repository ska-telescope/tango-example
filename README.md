SKA Skeleton Project
====================

Briefly describe your project here

Install 
-------

**Always** use a virtual environment. [Pipenv](https://pipenv.readthedocs.io/en/latest/) is now Python's officially
recommended method and the one used by default in this repo. **WARNING:** `requirements.txt` will be deprecated and
removed from this repo in the future.

Follow these steps at the project root:

```bash
pip install pipenv # if you don't have pipenv already installed on your system
pipenv install
pipenv shell
```

You will now be inside a pipenv shell with your virtual environment ready.

Use `pipenv exit` to exit the virtual environment.


Testing
-------

* Put tests into the `tests` folder
* Use [PyTest](https://pytest.org) as the testing framework
  - Reference: [PyTest introduction](http://pythontesting.net/framework/pytest/pytest-introduction/)
* Run tests with `python setup.py test`
  - Configure PyTest in `setup.py` and `setup.cfg`
* Running the test creates the `htmlcov` folder
    - Inside this folder a rundown of the issues found will be accessible using the `index.html` file
* All the tests should pass before merging the code 
 
 Code analysis
 -------------
 * Use [Pylint](https://www.pylint.org) as the code analysis framework
 * By default it uses the [PEP8 style guide](Python's PEP8 style guide)
 * Use the provided `code-analysis.sh` script in order to run the code analysis in the `module` and `tests`
 * Code analysis should only raise document related warnings (i.e. `#FIXME` comments) before merging the code