import json

SECONDS_PER_DAY = 86400
START_TIME = 1500000000

def associate(host_num, node_num, num_days):
    """Associate a host with a node (hardware configuration)
    for a certain amount of time"""
    end_time = currentTimeOf[host_num] + num_days*SECONDS_PER_DAY
    for record_time in range(currentTimeOf[host_num], end_time, SECONDS_PER_DAY):
        newRow = [hosts[host_num]] + nodes[node_num] + [record_time]
        result.append(newRow)
    currentTimeOf[host_num] = end_time


result = [
    [
        'hostname',
        'manufacturer',
        'codename',
        'model_name',
        'clock_speed',
        'core_count',
        'board_manufacturer',
        'board_name',
        'board_version',
        'system_manufacturer',
        'system_name',
        'system_version',
        'physmem',
        'disk_count',
        'ib_device_count',
        'ib_device',
        'ib_ca_type',
        'ib_ports',
        'gpu_device_count',
        'gpu_device_manufacturer',
        'gpu_device_name',
        'record_time',
    ]
]

hosts = [
    "cpn-k10-06-02",
    "cpn-m28-18-02",
]

currentTimeOf = []
for host_num in range(len(hosts)):
    currentTimeOf.append(START_TIME)

nodes = [
    [
        "INTEL",
        "Westmere EP",
        "Intel(R) Xeon(R) CPU E5645",
        "2.40GHz",
        12,
        "NA",
        "NA",
        "NA",
        "Dell",
        "C6100",
        "NA",
        48127,
        2,
        1,
        "qib0",
        "InfiniPath_QLE7340",
        1,
        0,
        "NA",
        "NA",
    ], [
        "INTEL",
        "Ivy Bridge EP",
        "Intel(R) Xeon(R) CPU E5-2650 v2",
        "2.60GHz",
        16,
        "NA",
        "NA",
        "NA",
        "HP",
        "ProLiant SL230s Gen8",
        "NA",
        64223,
        1,
        1,
        "mlx4_0",
        "MT4099",
        2,
        0,
        "NA",
        "NA",
    ]
]

associate(0, 0, 7)
associate(0, 1, 5)
associate(0, 0, 10)
associate(0, 0, 20)

associate(1, 1, 2)
associate(1, 0, 10)
associate(1, 1, 33)

print(json.dumps(result, indent=4, separators=(',', ': ')))