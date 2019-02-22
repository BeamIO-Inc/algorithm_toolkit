import distro
import pkg_resources
import platform
import psutil


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def vital_stats():
    vitals = {}
    system = platform.system()
    if system == 'Darwin':
        os = 'Mac OS ' + platform.mac_ver()[0]
    elif system == 'Windows':
        os = 'Windows ' + ' '.join(str(x) for x in platform.win32_ver())
    elif system == 'Linux':
        os = ' '.join(str(x) for x in distro.linux_distribution())
    elif system == 'Java':
        os = 'Java ' + platform.java_ver()[0]
    else:
        os = platform.platform()
    vitals['os'] = os
    vitals['python'] = platform.python_version()
    vitals['atk'] = pkg_resources.get_distribution('algorithm_toolkit').version
    vitals['cpu'] = psutil.cpu_percent(interval=0.1, percpu=True)

    disk_stats = psutil.disk_usage('/')
    vitals['disk'] = {
        'free': bytes2human(disk_stats.free),
        'percent': disk_stats.percent,
        'total': bytes2human(disk_stats.total),
        'used': bytes2human(disk_stats.used)
    }

    mem_stats = psutil.virtual_memory()
    vitals['mem'] = {
        'used': mem_stats.used,
        'percent': mem_stats.percent
    }

    return vitals
