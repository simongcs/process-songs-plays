# Process songs plays

This is an API REST where you can upload a csv file with columns ["song", "date", "number of plays" ] to summarize the total number of plays by date and get a resulting csv ["song", "date", "total number of plays" ]



## Requirements:

### virtualenv managment tool: pipenv
##### installing pipenv:
    pip install --user pipenv

### installing dependencies

    pipenv install 

## Run tests

    pytest

## Run the server

### enter the virtualenv

    pipenv shell

### run the app server

    python main.py




