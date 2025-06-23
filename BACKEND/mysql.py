# --- Mửa rộng: Import thêm các thư viện ---
from pyzabbix import ZabbixAPI
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, ForeignKey, select, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import time

# --- Cấu hình Zabbix ---
ZABBIX_URL = "http://172.16.1.43/zabbix"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"

# --- Cấu hình MySQL ---
DB_HOST = "172.16.0.91"
DB_PORT = 3306
DB_USER = "DATA"
DB_PASSWORD = "Khuongphuc123"
DB_NAME = "zabbix_data"

# --- Kết nối DB ---
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()

# --- Định nghĩa bảng ---
hosts_table = Table("hosts", metadata,
    Column("hostid", String(64), primary_key=True),
    Column("host", String(255)),
)

items_table = Table("items", metadata,
    Column("itemid", String(64), primary_key=True),
    Column("hostid", String(64), ForeignKey("hosts.hostid")),
    Column("name", String(255)),
    Column("key_", String(255)),
    Column("category", String(50)),
)

history_table = Table("history", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("itemid", String(64), ForeignKey("items.itemid")),
    Column("clock", Integer),
    Column("value", Float),
)

# --- Tạo view chuyển đổi clock -> datetime và value -> GB (tuỳ chỉnh) ---
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

# --- Phân loại category ---
def classify_category(key_):
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

# --- Kết nối Zabbix ---
def connect_to_zabbix():
    zapi = ZabbixAPI(ZABBIX_URL)
    zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)
    print("✅ Kết nối Zabbix thành công")
    return zapi

# --- Lưu host ---
def insert_hosts(conn, hosts):
    for host in hosts:
        stmt = insert(hosts_table).values(
            hostid=host["hostid"], host=host["host"]
        ).on_duplicate_key_update(host=host["host"])
        conn.execute(stmt)

# --- Lưu items ---
def insert_items(conn, items):
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

# --- Lưu history ---
def insert_history(conn, history_records):
    if history_records:
        conn.execute(history_table.insert(), history_records)

# --- Hàm chính ---
def save_data():
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

                numeric_items = [item for item in items if int(item["value_type"]) in (0, 3)]
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

            # Tạo view sau khi insert
            conn.execute(text(create_view_sql))

        print("✅ Hoàn thành quá trình lưu dữ liệu!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

# --- CHẠY ---
if __name__ == "__main__":
    save_data()
