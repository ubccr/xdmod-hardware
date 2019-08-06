import json
import argparse
import os
import sys
import time
import datetime

SECONDS_PER_DAY = 86400
HW_TYPES = []
result = []
currentTimeOf = {}

STAGING_COLUMNS = [
    "hostname",
    "manufacturer",
    "codename",
    "model_name",
    "clock_speed",
    "core_count",
    "board_manufacturer",
    "board_name",
    "board_version",
    "system_manufacturer",
    "system_name",
    "system_version",
    "physmem",
    "numa_node_count",
    "disk_count",
    "ethernet_count",
    "ib_device_count",
    "ib_device",
    "ib_ca_type",
    "ib_ports",
    "gpu_device_count",
    "gpu_device_manufacturer",
    "gpu_device_name",
    "record_time_ts",
    "resource_name",
]

def associate(hostname, hw_type, num_days):
    """Associate a host with a hardware configuration
    for a certain amount of time
    If hw_type == -1, then associate the host with nothing
    (i.e. simulate missing data for that number of days)"""
    global HW_TYPES
    global result
    end_time = currentTimeOf[hostname] + num_days*SECONDS_PER_DAY
    if hw_type != -1:
        if hw_type not in HW_TYPES:
            raise KeyError('Unknown hw_type %d specified in config for host %s' % (hw_type, hostname))
        for record_time_ts in range(currentTimeOf[hostname], end_time, SECONDS_PER_DAY):
            newRow = [hostname] + HW_TYPES[hw_type] + [record_time_ts] + ['test_resource']
            result.append(newRow)
    currentTimeOf[hostname] = end_time

def getOptions():
    """ process comandline options """
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', help='Specify the path to the configuration file', required=True)

    parser.add_argument('-o', '--output', default='hardware_staging_test.json', help='Specify the name and path of the output json file')

    args = parser.parse_args()
    return vars(args)

def main():
    global HW_TYPES
    global result

    opts = getOptions()

    outputFilename = opts['output']

    conffile = os.path.abspath(opts['config'])
    with open(conffile, "r") as conffp:
        try:
            config = json.load(conffp)
        except ValueError as exc:
            raise Exception('Syntax error in %s.\n%s' % (conffile, str(exc)))

    START_TIME = int(time.mktime(datetime.datetime.strptime(config['start_date'], "%Y-%m-%d").timetuple()))
    result.append(STAGING_COLUMNS)
    HW_TYPES = config['hw_types']
    ASSOCIATIONS = config['associations']

    for hostname in ASSOCIATIONS:
        currentTimeOf[hostname] = START_TIME
        for association in ASSOCIATIONS[hostname]:
            hw_type = association['hw_type']
            num_days = association['num_days']
            associate(hostname, hw_type, num_days)

    with open(outputFilename, 'w') as outFile:
        outFile.write(json.dumps(result, indent=4, separators=(',', ': ')))

if __name__ == '__main__':
    main()
