
var node_mapping = require('./node_mapping.json');
var dmi_info = require('./dmi_cluster_info.json');
var hardware_info = require('./hardware.json');

var result = [
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
        'ib_ports'
    ]
];

var hostname;
var processor_info;
var clock_speed;

for (let i = 0; i < dmi_info.length; i++) {
    hostname = dmi_info[i].hostname.split('.')[0];

    let vendor = dmi_info[i].vendor;
    if (vendor === 'Dell Inc.') {
        vendor = 'Dell';
    }
    let product = dmi_info[i].product;
    if (vendor === 'HP' && product === 'ProLiant xxxxxx Gen8') {
        product = 'ProLiant SL230s Gen8';
    }

    if (node_mapping[hostname]) {
        node_mapping[hostname].system_manufacturer = vendor;
        node_mapping[hostname].system_name = product;
    }
}

for (let i = 0; i < hardware_info.length; i++) {
    hostname = hardware_info[i].hostname.split('.')[0];

    let info = node_mapping[hostname];

    if (!info) {
        continue;
    }

    info.core_count = hardware_info[i].ncpu;
    info.disk_count = hardware_info[i].ndisk;
    info.physmem = hardware_info[i].physmem;

    if (hardware_info[i].infiniband) {
        for (let device in hardware_info[i].infiniband) {
            if (hostname === 'cpn-u25-30' && device === 'bnxt_re0') {
                continue
            }
            info.ib_device = device;
            info.ib_ca_type = hardware_info[i].infiniband[device][1];
            info.ib_ports = hardware_info[i].infiniband[device][2];
        }
    }
}

var get = function (value, typehint='str') {
    if (value) {
        return value;
    }
    if (typehint === 'str') {
        return 'NA'
    } else {
        return -1;
    }
};

for (hostname in node_mapping) {
    if (node_mapping.hasOwnProperty(hostname)) {
        let info = node_mapping[hostname];

        processor_info = info.processor.split(' @ ');
        clock_speed = -1;
        if (processor_info.length > 1) {
            clock_speed = processor_info[1];
        }

        result.push([
            hostname,
            get(info.manufacturer),
            get(info.codename),
            processor_info[0],
            clock_speed,
            get(info.core_count, 'int'),
            'NA',
            'NA',
            'NA',
            get(info.system_manufacturer),
            get(info.system_name),
            'NA',
            get(info.physmem, 'int'),
            get(info.disk_count, 'int'),
            info.ib_device ? 1 : 0,
            get(info.ib_device),
            get(info.ib_ca_type),
            get(info.ib_ports, 'int'),
        ]);
    }
}

process.stdout.write(JSON.stringify(result, null, 4));
