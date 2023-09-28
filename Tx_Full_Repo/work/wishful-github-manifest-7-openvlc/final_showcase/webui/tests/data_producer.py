import zmq
import time
import datetime
import json
import random

ctrls = (
    'WIFI_A1',
    'WIFI_A2',
    'WIFI_TDMA',
    '6lowPAN',
    'LTE_TDMA',
    'LTE_virt',
    'LTE_nb',
)

ctx = zmq.Context()
socket = ctx.socket(zmq.PUB)
socket.connect('tcp://localhost:5506')


load = ['Off', 'Low', 'Medium', 'High']
nsu = []
for net in ctrls:
    # {"name": , "type": , "channel": , "load": , "active": },
    nsu.append({
        "name": net,
        "type": random.choice(['Wi-Fi', 'LTE-U', 'IEEE 802.15.4']),
        "channel": 1,
        "load": 'Medium',
        "active": True,
    })

last_nsu = datetime.datetime.now().timestamp()

try:
    while True:
        now = datetime.datetime.now().timestamp()
        for ctrl in ctrls:
            data = {
                "type": "monitorReport",
                "monitorType": "performance",
                "networkController": ctrl,
                "networkType": "80211",
                "monitorValue": {
                    "timestamp": now,
                    "PER": random.random(),
                    "THR": random.random() * 1e6,
                },
            }
            socket.send_multipart([
                b'monitorReport',
                json.dumps(data).encode('utf-8'),
            ])
            print(now, ctrl)
        # if (now - last_nsu) > 5:
        #     current = []
        #     for net in nsu:
        #         net['channel'] = random.randint(1, 14)
        #         net['load'] = random.choice(load)
        #         net['active'] = random.choice([True, False])
        #         current.append(net)
        #     socket.send_multipart([
        #         b'networkStatusUpdate',
        #         json.dumps(nsu).encode('utf-8'),
        #     ])
        time.sleep(1)
finally:
    socket.close()
