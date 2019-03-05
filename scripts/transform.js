/* eslint-env node */
var node_mapping = require('./node_mapping.json');

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
        'system_version'
    ]
];

var hostname;
var processor_info;
var clock_speed;

for (hostname in node_mapping) {
    if (node_mapping.hasOwnProperty(hostname)) {
        processor_info = node_mapping[hostname].processor.split(' @ ');
        clock_speed = -1;
        if (processor_info.length > 1) {
            clock_speed = processor_info[1];
        }

        result.push([hostname, node_mapping[hostname].manufacturer, node_mapping[hostname].codename, processor_info[0], clock_speed, -1, 'NA', 'NA', 'NA', 'NA', 'NA', 'NA']);
    }
}

process.stdout.write(JSON.stringify(result, null, 4));
