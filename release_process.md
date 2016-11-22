Release process
===============

Run tests on target brunch
--------------------------
    tox -epep8
    tox -epy35
    tox -edocs


Declare package version
-----------------------
In setup.py, bump the package version:

    version='X.X.X' to version='X.X.Y'


Cut off stable branch
---------------------

    git checkout -b vX.X.X-stable
    git push origin vX.X.X-stable


Create GitHub tag
-----------------

    Releases ---> Draft New Release
    Name: AIOService version X.X.X stable release


Collect changes from previous version
-------------------------------------

    git log --oneline --decorate


Build distribution package
--------------------------

    python setup.py bdist_wheel


Check install capability for the wheel
--------------------------------------

    virtualenv .test_venv
    source .test_venv/bin/activate
    pip install dist/aioservice-X.X.X-py2.py3-none-any.whl


Submit release to PYPI
----------------------

    python setup.py bdist_wheel upload
