from pyzabbix import ZabbixAPI
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, ForeignKey
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mysql import insert

# --- CẤU HÌNH ZABBIX ---
ZABBIX_URL = "http://192.168.1.96/zabbix"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"

# --- CẤU HÌNH MYSQL (trên máy ảo MySQL) ---
DB_HOST = "192.168.1.95"
DB_PORT = 3306
DB_USER = "DATA"
DB_PASSWORD = "Khuongphuc123"
DB_NAME = "zabbix_data"

# Tạo connection string
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Tạo engine với các tùy chọn kết nối
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,  # Số lượng connection trong pool
    max_overflow=10,  # Số lượng connection có thể vượt quá pool_size
    pool_timeout=30,  # Thời gian timeout khi lấy connection từ pool
    pool_recycle=1800,  # Tái sử dụng connection sau 30 phút
)

metadata = MetaData()

# --- ĐỊNH NGHĨA BẢNG ---
hosts_table = Table(
    "hosts", metadata,
    Column("hostid", String(64), primary_key=True),
    Column("host", String(255)),
)

items_table = Table(
    "items", metadata,
    Column("itemid", String(64), primary_key=True),
    Column("hostid", String(64), ForeignKey("hosts.hostid")),
    Column("name", String(255)),
    Column("key_", String(255)),
)

history_table = Table(
    "history", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("itemid", String(64), ForeignKey("items.itemid")),
    Column("clock", Integer),
    Column("value", Float),
)

# Tạo bảng nếu chưa có
metadata.create_all(engine)


def connect_to_zabbix():
    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)
        print("✅ Kết nối Zabbix thành công")
        return zapi
    except Exception as e:
        print(f"❌ Lỗi kết nối Zabbix: {str(e)}")
        raise


def insert_hosts(conn, hosts):
    """Insert hosts using UPSERT"""
    try:
        for host in hosts:
            insert_stmt = insert(hosts_table).values(
                hostid=host["hostid"],
                host=host["host"]
            )
            # Sử dụng ON DUPLICATE KEY UPDATE để update nếu record đã tồn tại
            on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                host=insert_stmt.inserted.host
            )
            conn.execute(on_duplicate_key_stmt)
        print(f"✅ Đã insert/update {len(hosts)} hosts")
    except SQLAlchemyError as e:
        print(f"❌ Lỗi khi insert hosts: {str(e)}")
        raise


def insert_items(conn, items):
    """Insert items using UPSERT"""
    try:
        for item in items:
            insert_stmt = insert(items_table).values(
                itemid=item["itemid"],
                hostid=item["hostid"],
                name=item["name"],
                key_=item["key_"]
            )
            on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                name=insert_stmt.inserted.name,
                key_=insert_stmt.inserted.key_
            )
            conn.execute(on_duplicate_key_stmt)
        print(f"✅ Đã insert/update {len(items)} items")
    except SQLAlchemyError as e:
        print(f"❌ Lỗi khi insert items: {str(e)}")
        raise


def insert_history(conn, history_records):
    """Insert history records in bulk"""
    try:
        if history_records:
            conn.execute(history_table.insert(), history_records)
            print(f"✅ Đã insert {len(history_records)} history records")
    except SQLAlchemyError as e:
        print(f"❌ Lỗi khi insert history: {str(e)}")
        raise


def save_data():
    try:
        # Kết nối Zabbix
        zapi = connect_to_zabbix()
        
        # Lấy danh sách hosts
        hosts = zapi.host.get(output=["hostid", "host"])
        
        # Sử dụng context manager để tự động đóng connection
        with engine.begin() as conn:
            # Insert hosts
            insert_hosts(conn, hosts)
            
            # Xử lý từng host
            for host in hosts:
                # Lấy items của host
                items = zapi.item.get(
                    hostids=[host["hostid"]],
                    output=["itemid", "name", "key_","hostid"],
                    monitored=True
                )
                
                # Insert items
                insert_items(conn, items)
                
                # Xử lý history cho từng item
                for item in items:
                    end_time = int(time.time())
                    start_time = end_time - 3600  # 1 giờ
                    
                    history = zapi.history.get(
                        itemids=[item["itemid"]],
                        time_from=start_time,
                        time_till=end_time,
                        output="extend",
                        sortfield="clock",
                        sortorder="ASC"
                    )
                    
                    # Chuẩn bị dữ liệu history để insert
                    history_records = []
                    for h in history:
                        try:
                            history_records.append({
                                "itemid": item["itemid"],
                                "clock": int(h["clock"]),
                                "value": float(h["value"])
                            })
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ Bỏ qua record không hợp lệ: {str(e)}")
                            continue
                    
                    # Insert history records
                    if history_records:
                        insert_history(conn, history_records)
        
        print("✅ Hoàn thành quá trình lưu dữ liệu!")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình lưu dữ liệu: {str(e)}")
        raise


if __name__ == "__main__":
    save_data()