# WiSHFUL final showcase UI

## Install & Running

To install:
```
pipenv install
```

To run:

```
pipenv shell bokeh serve --allow-websocket-origin="*:5006" wishful
```

For testing start additionally:

```
pipenv shell python tests/data_producer.py
```

## Message template

```json
{
    "type": "monitorReport",
    "monitorType": "performance",
    "networkController": "WIFI_CNIT",
    "networkType":"80211",
    "monitorValue": {
        "timestamp": 1522169960.4682555,
        "PER": 0.0030952405906813363,
        "THR": 8760.0}
    },
}
```
