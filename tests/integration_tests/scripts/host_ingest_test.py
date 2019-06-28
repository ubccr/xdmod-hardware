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

def associate(hostname, hw_num, num_days):
    """Associate a host with a hardware configuration
    for a certain amount of time
    If hw_num == -1, then associate the host with nothing
    (i.e. simulate missing data for that number of days)"""
    global HW_TYPES
    global result
    end_time = currentTimeOf[hostname] + num_days*SECONDS_PER_DAY
    if hw_num != -1:
        for record_time_ts in range(currentTimeOf[hostname], end_time, SECONDS_PER_DAY):
            newRow = [hostname] + HW_TYPES[hw_num] + [record_time_ts] + ['test_resource']
            result.append(newRow)
    currentTimeOf[hostname] = end_time

def getOptions():
    """ process comandline options """
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', help='Specify the path to the configuration directory', required=True)

    parser.add_argument('-o', '--output', default='hardware_staging_test.json', help='Specify the name and path of the output json file')

    args = parser.parse_args()
    return vars(args)

def main():
    global HW_TYPES
    global result

    opts = getOptions()

    outputFilename = opts['output']

    confpath = opts['config']
    conffile = os.path.join(confpath, "test_data.json")
    with open(conffile, "r") as conffp:
        try:
            config = json.load(conffp)
        except ValueError as exc:
            raise Exception('Syntax error in %s.\n%s' % (conffile, str(exc)))

    START_TIME = int(time.mktime(datetime.datetime.strptime(config['start_date'], "%Y-%m-%d").timetuple()))
    result.append(config['column_names'])
    HW_TYPES = config['hw_types']
    ASSOCIATIONS = config['associations']

    for hostname in ASSOCIATIONS:
        currentTimeOf[hostname] = START_TIME
        for association in ASSOCIATIONS[hostname]:
            hw_num = association['hw_num']
            num_days = association['num_days']
            if hw_num >= len(HW_TYPES) or hw_num < -1:
                raise IndexError('hw_num %d in config for host %s is illegal, %d hw_types were given in config' % (hw_num, hostname, len(HW_TYPES)))
            associate(hostname, hw_num, num_days)

    with open(outputFilename, 'w') as outFile:
        outFile.write(json.dumps(result, indent=4, separators=(',', ': ')))

if __name__ == '__main__':
    main()
