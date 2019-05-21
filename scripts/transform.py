import json, sys
from re import sub, search
from collections import OrderedDict

REPLACEMENT_RULES_FILE = 'replacement_rules.json'
if len(sys.argv) > 1 and sys.argv[1] == "-t":
    REPLACEMENT_RULES_FILE = 'replacement_rules_test.json'

def loadJson(jsonFile, object_pairs_hook=None):
    """Loads a json file, returns whatever python object is in the file
    Optional arguments are the same as in json.load"""
    with open(jsonFile, 'r') as inFile:
        return json.load(inFile, object_pairs_hook=object_pairs_hook)

try:
    node_mapping = loadJson('node_mapping.json', object_pairs_hook=OrderedDict)
    dmi_info = loadJson('dmi_cluster_info.json')
    hardware_info = loadJson('hardware.json')
except IOError as e:
    print('File not found: ' + e.filename)
    exit()

try:
    replacementRules = loadJson(REPLACEMENT_RULES_FILE, object_pairs_hook=OrderedDict)
except IOError as e:
    replacementRules = []

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
        'record_time'
    ]
]

# Build a dictionary mapping column names to index
columnToIndex = {}
for i in range(len(result[0])):
    columnToIndex[result[0][i]] = i

for cluster in dmi_info:
    hostname = cluster['hostname'].split('.')[0]

    vendor = cluster['vendor']
    product = cluster['product']

    ##########################################
    # Hardcoded conformation                 #
    ##########################################

    # if vendor == 'Dell Inc.':
    #     vendor = 'Dell'
    
    # if (vendor == 'HP' and product == 'ProLiant xxxxxx Gen8'):
    #     product = 'ProLiant SL230s Gen8'

    ###########################################

    if hostname in node_mapping:
        node_mapping[hostname]['system_manufacturer'] = vendor
        node_mapping[hostname]['system_name'] = product
    
hardware_info.sort(key = lambda x: (x['hostname'], x['time']))

for hw_info in hardware_info:
    hostname = hw_info['hostname'].split('.')[0]
    
    info = node_mapping.get(hostname)

    if (info == None):
        continue

    info['core_count'] = hw_info['ncpu']
    info['disk_count'] = hw_info['ndisk']
    info['physmem'] = hw_info['physmem']
    info['record_time'] = hw_info['time']

    if 'infiniband' in hw_info:
        for device in hw_info['infiniband']:
            ##########################################
            # Hardcoded conformation                 #
            ##########################################
            
            # if (hostname == 'cpn-u25-30') and (device == 'bnxt_re0'):
            #     continue

            ###########################################
            info['ib_device'] = device
            info['ib_ca_type'] = hw_info['infiniband'][device][1]
            info['ib_ports'] = hw_info['infiniband'][device][2]

    if ('gpu' in hw_info) and ('gpu0' in hw_info['gpu']):
        devices = list(hw_info['gpu'])
        info['gpu_device_count'] = len(devices)
        info['gpu_device_manufacturer'] = 'NA'
        # info['gpu_device_manufacturer'] = 'Nvidia'
        info['gpu_device_name'] = hw_info['gpu']['gpu0']
    elif 'gpu_device_count' not in info:
        info['gpu_device_count'] = 0

def get(value, typehint='str'):
    if (value != None) and (value != ""):
        return value
    if typehint == 'str':
        return 'NA'
    else:
        return -1

for hostname in node_mapping:
    if hostname in node_mapping:    # this condition should be changed or eliminated
        info = node_mapping[hostname]

        processor_info = info['processor'].split(' @ ')
        clock_speed = -1
        if (len(processor_info) > 1):
            clock_speed = processor_info[1]

        result.append([
            hostname,
            get(info.get('manufacturer')),
            get(info.get('codename')),
            processor_info[0],
            clock_speed,
            get(info.get('core_count'), 'int'),
            'NA',
            'NA',
            'NA',
            get(info.get('system_manufacturer')),
            get(info.get('system_name')),
            'NA',
            get(info.get('physmem'), 'int'),
            get(info.get('disk_count'), 'int'),
            1 if ('ib_device' in info) else 0,
            get(info.get('ib_device')),
            get(info.get('ib_ca_type')),
            get(info.get('ib_ports'), 'int'),
            info['gpu_device_count'],
            get(info.get('gpu_device_manufacturer')),
            get(info.get('gpu_device_name')),
            get(info.get('record_time'))
        ])

        # Replacement
        row = result[-1]
        for rule in replacementRules:
            # Check if conditions are true
            conditionsMet = True
            if 'conditions' in rule:
                for condition in rule['conditions']:
                    assert 'column' in condition, 'Conditions must contain a "column" entry'
                    value = row[columnToIndex[condition['column']]]
                    reverse = ('reverse' in condition) and (condition['reverse']) # If 'reverse' is true, then the condition must be FALSE to replace
                    # Case one: equality condition
                    if 'equals' in condition:
                        if (condition['equals'] != value) != reverse:
                            conditionsMet = False
                            break
                    # Case two: contains condition
                    else:
                        assert 'contains' in condition, 'Conditions must contain either an "equals" or a "contains" property'
                        if (search(condition['contains'], value) == None) != reverse:
                            conditionsMet = False
                            break
            # Process replacements
            if conditionsMet:
                assert 'replacements' in rule, "Rules must contain a 'replacements' entry"
                for replacement in rule['replacements']:
                    assert 'column' in replacement, "Replacements must contain a 'column' entry"
                    assert 'repl' in replacement, "Replacements must contain a 'repl' entry"
                    index = columnToIndex[replacement['column']]
                    # Case one: regex pattern replacement
                    if 'pattern' in replacement:
                        row[index] = sub(replacement['pattern'], replacement['repl'], row[index])
                    # Case two: replace whole value
                    else:
                        row[index] = replacement['repl']

print(json.dumps(result, indent=4, separators=(',', ': ')))
