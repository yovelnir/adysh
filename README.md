# ADYSH

# Description

ADYSH is a warehouse management system for academic design departments.
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pipenv.

```bash
pip install pipenv
```

Enter directory adivtest under ADYSH folder

```bash
cd adivtest
```
Enter the pipenv shell

```bash
pipenv shell
```

Use the package manager pipenv to install the following: django, pyrebase4, firebase-admin, reportlab

```pipenv
pipenv install django
```
```pipenv
pipenv install pyrebase4
```
```pipenv
pipenv install firebase-admin
```
```pipenv
pipenv install reportlab
```

## Usage
Inside the pipenv shell terminal run the Django server
```pipenv
python manage.py runserver
```
The url of the server will be printed in terminal output
```
System check identified no issues (0 silenced).
January 14, 2023 - 14:34:30
Django version 4.1.5, using settings 'adivtest.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
