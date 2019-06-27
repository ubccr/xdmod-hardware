---
title: Replacement Rules
---

The file `replacement_rules.json` describes rules to selectively edit 
the output of `get_hardware_info.py`. This script generates a json file 
representing the staging table for the hardware xdmod database. Each
rule specified in `replacement_rules.json` can alter the data in a certain column,
to either make the data more consistent, add missing data, or fix data that is incorrect.

`replacement_rules.json` consists of a list of rules which are applied to every row in the
output table, in order. A rule consists of two properties: `conditions`, which must be met 
in order for the rule to be applied, and `replacements`, which describe exactly what data to replace.
If the `conditions` property is missing, then the replacement will be applied to every row.

Here is a simple example of a rule:

```json
{
    "replacements":[
        {
            "column": "manufacturer",
            "pattern": "GenuineIntel",
            "repl": "INTEL"
        },
        {
            "column": "manufacturer",
            "pattern": "AuthenticAMD",
            "repl": "AMD"
        }
    ]
}
```

Note that this rule does not have any conditions, and so it will be applied to every row. 
The effect of this rule is that rows with a manufacturer of `GenuineIntel` will be 
changed to `INTEL`, and likewise `AuthenticAMD` will be changed to `AMD`.

The `replacements` property contains a list of replacements to apply. Each replacement 
has up to three properties:
- `column`: the entry in the row that should be changed by the replacement
- `pattern`: a regex search pattern to use for replacement. If absent, then the entire entry will be replaced.  
  - Note that if specified, replacement will only occur if a pattern match is found in the entry
- `repl`: the value to replace with

Below is another rule which contains a condition:

```json
{
    "conditions":[
        {
            "column": "system_manufacturer",
            "equals": "HP"
        }
    ],
    "replacements":[
        {
            "column": "system_name",
            "pattern": "ProLiant xxxxxx Gen8",
            "repl": "ProLiant SL230s Gen8"
        }
    ]
}
```

This rule will only act on rows where the `system_manufacturer` column is `"HP"`,
and it will replace a `system_name` of `"ProLiant xxxxxx Gen8"` with `"ProLiant SL230s Gen8"`

The `conditions` property contains a list of conditions, all of which must be met
in order for the replacement to occur. Each condition can contain the following properties:
- `column`: the entry in the row to check
- One of two mutually exclusive options:
  - `equals`: the condition is met if the specified entry contains exactly this text
  - `contains`: the condition is met if the entry contains this regex search pattern
- `reverse`: `false` by default. If `true`, then the truth value of the condition is reversed.
  - For example, if `equals` is used when `reverse` is `true`, then the condition will be met if and only if the entry does NOT equal the specified value

The following example is a more complicated rule:

```json
{
    "conditions":[
        {
            "column": "gpu_device_count",
            "equals": 0,
            "reverse": true
        },
        {
            "column": "gpu_device_count",
            "equals": -1,
            "reverse": true
        }
    ],
    "replacements":[
        {
            "column": "gpu_device_manufacturer",
            "repl": "Nvidia"
        }
    ]
}
```

This rule will set the `gpu_device_manufacturer` entry to `"Nvidia"` for any row in which
the `gpu_device_count` entry does NOT equal 0 or -1.