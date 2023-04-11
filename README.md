# ASTERISK_CONNECTOR
### Requirements
- python3.10
- Flask==2.2.2
- redis==4.4.2

## Installation

#### Install ami parser
```
cd ami_parser
python3 setup.py install
```

#### Install call_maker
```
cd call_maker
python3 setup.py install
```

#### Install requirements
```
pip install requrements.txt
```

### AMI PARSER
This app connects to AMI TCP socket and parse call events

### CALL MAKER
Simple request handler which based on Flask. App connects to AMI TCP socket and sends originate actions to initialize call between two participants.
#### usage
This App handles GET request by URI: /make_call with params
- num_src - manager`s inner phone number
- num_dst - client number
- project - project abbr. This param needs for send stats to CNET. Can be optional if env variable AGGR_STATS=0

##### Example:
```
https://127.0.0.1:5000/make_call?num_src=109&num_dst=790001112223
```

### START APP
This App used enviroment variables
- REDIS_URL - connection string like 'redis://localhost:6379/0'
- APP_PORT - port wich application listening. 5000 by default
- AMI_HOST - asterisk host
- AMI_PORT - 5038 by default
- AMI_USER
- AMI_SECRET
- AGGR_STATS - 1 or 0. 0 by default. This varible enables stats collection (ami_parser module) and can send statistics to CNET to our projects. CNET_URLS writes in call_maker.constants

```
cd asterisk-connector
REDIS_URL='redis://127.0.0.1:6379/0' AMI_HOST='vipsip.alrem.pp.ua' AMI_PORT=5038 AMI_USER='kingz' AMI_SECRET='gjhjctyjr26' AGGR_STATS=0 python3 app.py
```

