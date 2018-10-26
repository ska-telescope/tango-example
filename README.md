SKA Skeleton Project
====================

Briefly describe your project here

Install 
-------

How to install 

Testing
-------

* **Always** use a virtual environment like `virtualenv` or `anaconda`
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