# PRadReader code (Proton Radiography Reader)
PRadReader code
# Setup

## Dependencies
This module requires **Python 2.7** or **3.5**. Installation requires **git**.

**OS X users:** Prior to installing dependencies, ensure an adequate Python installation by following [this guide](https://matplotlib.org/faq/installing_faq.html#osx-notes). The Python that ships with OS X may not work well with some required dependencies.

The following Python packages are required:
* future (Cross-compatibility between Python2 and Python3)
* numpy (Scientific computing)
* matplotlib (Plotting)
* pandas (Parsing Large files)

On most systems (see above note for OS X), they can be installed using Python's [PIP package manager](https://packaging.python.org/tutorials/installing-packages/) as follows:

```shell
pip install future
pip install numpy pandas
```
Depending on how Python was installed on your system, `pip` may require *Administrative* or `sudo` privileges.

## Installation
Once all dependencies are satisfied, install the latest version of **PRadReader** by:

```shell
pip install git+https://github.com/flash-center/PRadReader
```

The module can also be installed by:

```shell
git clone https://github.com/flash-center/PRadReader
cd PRadReader
python setup.py install
```
Alternatively, if you do not have root permissions, install the package to your user directory:

```bash
python setup.py install --user
```

