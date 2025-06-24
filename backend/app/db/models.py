"""
Database models for the Zabbix AI Anomaly Detection application
"""
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey

metadata = MetaData()

# Host table
hosts_table = Table(
    "hosts",
    metadata,
    Column("hostid", String(64), primary_key=True),
    Column("host", String(255)),
)

# Items table
items_table = Table(
    "items",
    metadata,
    Column("itemid", String(64), primary_key=True),
    Column("hostid", String(64), ForeignKey("hosts.hostid")),
    Column("name", String(255)),
    Column("key_", String(255)),
    Column("category", String(50)),
)

# History table
history_table = Table(
    "history",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("itemid", String(64), ForeignKey("items.itemid")),
    Column("clock", Integer),
    Column("value", Float),
)

# Feedback table
feedbacks_table = Table(
    "feedbacks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("hostid", String(50)),
    Column("item", String(255)),
    Column("feedback", String(50)),
    Column("comment", String(255)),
    Column("timestamp", String(50)),
)

# SQL for creating a readable view of history data
create_view_sql = """
CREATE OR REPLACE VIEW history_readable AS
SELECT 
    h.id,
    h.itemid,
    i.name,
    i.key_,
    i.category,
    FROM_UNIXTIME(h.clock) AS time,
    ROUND(h.value / POWER(1024, 3), 2) AS value_in_gb
FROM history h
JOIN items i ON h.itemid = i.itemid;
""" 