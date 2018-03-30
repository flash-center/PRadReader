# PRadReader code (Proton Radiography Reader)

PRadReader is intended to provide an interface to read in various experimental and simulated proton radiography flux data for analysis with the Python libraries
[PRaLine](https://github.com/flash-center/PRaLine) and [PROBLEM](https://github.com/flash-center/PROBLEM).

The typical workflow for PRadReader and PRaLine/PROBLEM is as follows:

![Workflow](images/workflow.png)

PRadReader takes various experimental and simulated proton radiography data, reads it, prompts the user for additional experimental setup data (including relevant distances from the source to the plasma, across the plasma, etc.) and compiles it into a PRR data file.
PRaLine and PROBLEM both include command line tools to read in PRR data files to perform their reconstruction algorithms with the data inside.

The currently supported formats are: FLASH4 output, MIT csv, and regular csv files with the radiography flux data inside.



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
## Usage

PRadReader includes a commmand line tool `pradreader` to automatically handle reading experimental and simulated proton radiography data for the supported formats listed above. 
In order to use it, first install PRadReader and then type

```bash
pradreader myfile.ext -o prr_file.txt
```

to read the file `myfile.ext`. PRadReader will then prompt you for the file type (FLASH4, MIT, csv) and will prompt you for the relevant distances and other information needed for the reconstruction process. It will save a PRR data file to the output `prr_file.txt`. Then, using PRaLine or PROBLEM, you can use `prr_file.txt` to complete your analysis of the radiography flux data.
