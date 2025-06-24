# main_api.py

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import pandas as pd
import json
import google.generativeai as genai
from pyzabbix import ZabbixAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, insert, text, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# ================= CONFIG ==================
ZABBIX_URL = "http://172.16.0.142/zabbix"
ZABBIX_USER = "Admin"
ZABBIX_PASSWORD = "zabbix"
GEMINI_API_KEY = "AIzaSyCy4T4o301ih--BgVeYddIaXaUKwElAKmo"

# MySQL
DB_URL = "mysql+pymysql://DATA:Khuongphuc123@172.16.0.91:3306/zabbix_data"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()

# ================== TABLES ==================
feedbacks_table = Table(
    "feedbacks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("hostid", String(50)),
    Column("item", String(255)),  # Optional: you can leave as NULL
    Column("feedback", String(50)),
    Column("comment", String(255)),
    Column("timestamp", String(50)),
)

SessionLocal = sessionmaker(bind=engine)

# ================= INIT ====================
app = FastAPI()
genai.configure(api_key=GEMINI_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dùng cho dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Feedback(BaseModel):
    host_id: str
    feedback: str
    comment: str

class HostRequest(BaseModel):
    host_ids: List[str]
    time_period: int = 24


def connect_to_zabbix():
    zapi = ZabbixAPI(ZABBIX_URL)
    zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)
    return zapi


def call_gemini_api(prompt):
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(prompt)
    return response.text


@app.post("/submit_feedback")
async def submit_feedback(feedback: Feedback):
    session = SessionLocal()
    try:
        stmt = insert(feedbacks_table).values(
            hostid=feedback.host_id,
            feedback=feedback.feedback,
            comment=feedback.comment,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        session.execute(stmt)
        session.commit()
        return {"status": "Feedback saved to MySQL"}
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
@app.get("/chart_data")
async def get_chart_data(host_id: str = Query(...), category: str = Query(...)):
    session = SessionLocal()
    try:
        query = text("""
            SELECT i.name, h.time, h.value_in_gb
            FROM history_readable h
            JOIN items i ON h.itemid = i.itemid
            WHERE i.hostid = :host_id AND i.category = :category
            ORDER BY h.time ASC
        """)
        result = session.execute(query, {"host_id": host_id, "category": category})
        rows = result.fetchall()
        return [
            {
                "metric": row[0],
                "time": row[1].strftime("%Y-%m-%d %H:%M:%S"),
                "value": row[2]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
@app.get("/get_hosts")
async def get_hosts():
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT hostid, host FROM hosts"))
        return [{"hostid": r[0], "host": r[1]} for r in result.fetchall()]
    finally:
        session.close()



@app.post("/detect_anomalies")
async def detect_anomalies(host_id: str, time_period: int = 24):
    try:
        zapi = connect_to_zabbix()
        host = zapi.host.get(hostids=[host_id], output=["host"])[0]
        items = zapi.item.get(hostids=[host_id], output=["itemid", "name"], monitored=True)

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_period)

        all_history = []
        for item in items[:20]:
            history = zapi.history.get(
                itemids=[item["itemid"]],
                time_from=int(start_time.timestamp()),
                time_till=int(end_time.timestamp()),
                output="extend",
                sortfield="clock",
                sortorder="ASC"
            )
            for h in history:
                all_history.append({
                    "item_name": item["name"],
                    "value": h["value"],
                    "timestamp": h["clock"],
                })

        df = pd.DataFrame(all_history)

        prompt = f"""
        Analyze the following monitoring data from Zabbix:

        Host: {host['host']}
        Time: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}
        Data:
        {df.to_string(index=False)}

        Return in JSON:
        {{
            "anomalies": [{{"metric": "...", "severity": "...", "cause": "...", "action": "..."}}]
        }}
        """

        response_text = call_gemini_api(prompt)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        return json.loads(response_text[json_start:json_end])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/root_cause_analysis")
async def root_cause_analysis(host_id: str, time_period: int = 24):
    try:
        zapi = connect_to_zabbix()
        host = zapi.host.get(hostids=[host_id], output=["host"])[0]
        items = zapi.item.get(hostids=[host_id], output=["itemid", "name"], monitored=True)

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_period)

        all_history = []
        for item in items[:10]:
            history = zapi.history.get(
                itemids=[item["itemid"]],
                time_from=int(start_time.timestamp()),
                time_till=int(end_time.timestamp()),
                output="extend",
                sortfield="clock",
                sortorder="ASC"
            )
            for h in history:
                all_history.append({
                    "item_name": item["name"],
                    "value": h["value"],
                    "timestamp": h["clock"],
                })

        df = pd.DataFrame(all_history)

        prompt = f"""
        You are a monitoring expert. Below is Zabbix data:
        Host: {host['host']}
        Time: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}
        Data:
        {df.to_string(index=False)}

        Return JSON:
        {{
            "root_cause": "...",
            "evidence": ["..."],
            "confidence": "High",
            "recommendation": "..."
        }}
        """

        response_text = call_gemini_api(prompt)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        return json.loads(response_text[json_start:json_end])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
