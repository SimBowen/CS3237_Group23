# Up-Goer

We externalise your sense of posture so that you can lead a healthier, less painful life.

We do this by providing a real-time feedback of your posture.
Simply wear a vest that comes equipped with 3 CC2650STK sensor tags and enjoy a real-time feed of your posture.
When your posture is less than ideal, we prompt you with a blaring red flag.

## Usage

- To discover bluetooth addresses
  `up-goer discover`
- To start the gateway for one sensor
  `up-goer gateway-single <address: string>`
- To start the gateway for multiple sensors
  `up-goer gateway-all`
- To start the computer
  `up-goer computer`
- To log data from the gateway
  `up-goer generate-csv <filename: Path>`
- To send prior gateway data to the server
  `up-goer generate-csv <filename: Path>`
- To observe prediction data from the server
  `up-goer observe-server`

## Setup

1. Install [Poetry](https://python-poetry.org/)
2. cd into this repository.
3. Run `poetry install`
4. Create a .env file with the following properties

```
SERVER_PASSWORD=PASSWORD
```

## Optional setup

Note: without doing this you have to prefix each of the commands with `poetry run`

1. Install [direnv](https://github.com/direnv/direnv)
2. Create a .envrc file with

```
layout python
```

3. execute `direnv allow`
