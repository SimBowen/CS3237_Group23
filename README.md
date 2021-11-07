# CS3237
## Setup
1. Install [Poetry](https://python-poetry.org/)
2. cd into this repository before executing any poetry commands.
3. Run `poetry install`
4. Create a .env file with the following properties
```
SERVER_PASSWORD=PASSWORD
```

## Usage
* To discover bluetooth addresses, execute `poetry run up_goer discover`
* To start the gateway, execute `poetry run up_goer gateway`
* To start the computer, execute `poetry run up_goer computer`
* To start the logger, execute `poetry run up_goer logger`

## Optional setup to eliminate poetry run
1. Install [direnv](https://github.com/direnv/direnv)
2. Createa  .envrc file with
```
layout python
```
Now you can call up_goer <command>