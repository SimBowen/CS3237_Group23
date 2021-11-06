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
* To start the gateway, execute `poetry run up_goer gateway`
* To discover bluetooth addresses, execute `poetry run up_goer discover`