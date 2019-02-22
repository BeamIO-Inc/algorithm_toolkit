# {{ alg['display_name'] }}
{{ alg['description'] }}
Version: {{ alg['version'] }}
License: {{ alg['license'] }}
Homepage: [{{ alg['homepage'] }}]

## Parameters:
Name|Description|Required
---|---|:---:
{% for rp in alg['required_parameters'] %}{{ rp['name'] }}|{{ rp['description'] }}|Yes
{% endfor %}{% for op in alg['optional_parameters'] %}{{ op['name'] }}|{{ op['description'] }}|
{% endfor %}
## Outputs:
Name|Description
---|---
{% for out in alg['outputs'] %}{{ out['name'] }}|{{ out['description'] }}
{% endfor %}
