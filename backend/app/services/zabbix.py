"""
Zabbix service for interacting with the Zabbix API
"""
from pyzabbix import ZabbixAPI
from datetime import datetime, timedelta

from ..core.config import ZABBIX_URL, ZABBIX_USER, ZABBIX_PASSWORD


def connect_to_zabbix():
    """
    Connect to the Zabbix API
    """
    zapi = ZabbixAPI(ZABBIX_URL)
    zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)
    return zapi


def classify_category(key_):
    """
    Classify an item key into a category
    """
    if key_.startswith("system.cpu"):
        return "CPU"
    elif key_.startswith("vm.memory") or "memory" in key_:
        return "Memory"
    elif key_.startswith("vfs.fs."):
        return "Disk"
    elif key_.startswith("net.if") or key_.startswith("net."):
        return "Network"
    elif key_.startswith("service.info"):
        return "Service"
    return "Other"


def get_hosts():
    """
    Get all hosts from Zabbix
    """
    zapi = connect_to_zabbix()
    return zapi.host.get(output=["hostid", "host"])


def get_host_items(host_id):
    """
    Get all items for a host from Zabbix
    """
    zapi = connect_to_zabbix()
    items = zapi.item.get(
        hostids=[host_id],
        output=["itemid", "name", "key_", "hostid", "value_type"],
        monitored=True,
    )

    # Filter for numeric items only
    return [item for item in items if int(item["value_type"]) in (0, 3)]


def get_history(item_id, time_period=24):
    """
    Get history for an item from Zabbix
    """
    zapi = connect_to_zabbix()
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=time_period)

    return zapi.history.get(
        itemids=[item_id],
        time_from=int(start_time.timestamp()),
        time_till=int(end_time.timestamp()),
        output="extend",
        sortfield="clock",
        sortorder="ASC"
    )