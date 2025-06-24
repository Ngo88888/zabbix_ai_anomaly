"""
Data service for syncing data from Zabbix to the local database
"""
from sqlalchemy import insert, text
from sqlalchemy.exc import SQLAlchemyError
import time
from datetime import datetime

from ..db.database import engine
from ..db.models import hosts_table, items_table, history_table, create_view_sql
from ..services.zabbix import connect_to_zabbix, classify_category


def insert_hosts(conn, hosts):
    """
    Insert hosts into the database
    """
    for host in hosts:
        stmt = insert(hosts_table).values(
            hostid=host["hostid"], host=host["host"]
        ).on_duplicate_key_update(host=host["host"])
        conn.execute(stmt)


def insert_items(conn, items):
    """
    Insert items into the database
    """
    for item in items:
        category = classify_category(item["key_"])
        stmt = insert(items_table).values(
            itemid=item["itemid"],
            hostid=item["hostid"],
            name=item["name"],
            key_=item["key_"],
            category=category,
        ).on_duplicate_key_update(
            name=item["name"], key_=item["key_"], category=category
        )
        conn.execute(stmt)


def insert_history(conn, history_records):
    """
    Insert history records into the database
    """
    if history_records:
        conn.execute(history_table.insert(), history_records)


def sync_data():
    """
    Synchronize data from Zabbix to the local database
    """
    try:
        zapi = connect_to_zabbix()
        hosts = zapi.host.get(output=["hostid", "host"])

        with engine.begin() as conn:
            insert_hosts(conn, hosts)
            for host in hosts:
                items = zapi.item.get(
                    hostids=[host["hostid"]],
                    output=["itemid", "name", "key_", "hostid", "value_type"],
                    monitored=True,
                )

                numeric_items = [
                    item for item in items if int(item["value_type"]) in (0, 3)
                ]
                insert_items(conn, numeric_items)

                for item in numeric_items:
                    value_type = int(item["value_type"])
                    history_type = 0 if value_type == 0 else 3
                    end_time = int(time.time())
                    start_time = end_time - 3600

                    history = zapi.history.get(
                        itemids=[item["itemid"]],
                        time_from=start_time,
                        time_till=end_time,
                        output="extend",
                        history=history_type,
                        sortfield="clock",
                        sortorder="ASC",
                    )

                    history_records = []
                    for h in history:
                        try:
                            history_records.append({
                                "itemid": item["itemid"],
                                "clock": int(h["clock"]),
                                "value": float(h["value"]),
                            })
                        except (ValueError, TypeError):
                            continue

                    insert_history(conn, history_records)

            # Create view after insert
            conn.execute(text(create_view_sql))

        print(f"✅ Data sync completed at {datetime.now()}")
        return True

    except Exception as e:
        print(f"❌ Data sync error: {e}")
        return False 