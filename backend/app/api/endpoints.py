"""
API endpoints for the Zabbix AI Anomaly Detection application
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import insert, text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from ..db.database import get_db
from ..db.models import feedbacks_table
from ..services.zabbix import connect_to_zabbix
from ..services.ai import detect_anomalies, analyze_root_cause

router = APIRouter()


class Feedback(BaseModel):
    """Feedback model"""
    host_id: str
    feedback: str
    comment: str


class HostRequest(BaseModel):
    """Host request model"""
    host_ids: List[str]
    time_period: int = 24


@router.get("/get_hosts")
async def api_get_hosts(db: Session = Depends(get_db)):
    """
    Get all hosts from the database
    """
    try:
        result = db.execute(text("SELECT hostid, host FROM hosts"))
        return [{"hostid": r[0], "host": r[1]} for r in result.fetchall()]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart_data")
async def api_get_chart_data(
    host_id: str = Query(...),
    category: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Get chart data for a host and category
    """
    try:
        query = text("""
            SELECT i.name, h.time, h.value_in_gb
            FROM history_readable h
            JOIN items i ON h.itemid = i.itemid
            WHERE i.hostid = :host_id AND i.category = :category
            ORDER BY h.time ASC
        """)
        result = db.execute(query, {"host_id": host_id, "category": category})
        rows = result.fetchall()
        return [
            {
                "metric": row[0],
                "time": row[1].strftime("%Y-%m-%d %H:%M:%S"),
                "value": row[2]
            }
            for row in rows
        ]
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit_feedback")
async def api_submit_feedback(
    feedback: Feedback,
    db: Session = Depends(get_db)
):
    """
    Submit feedback for an AI analysis
    """
    try:
        stmt = insert(feedbacks_table).values(
            hostid=feedback.host_id,
            feedback=feedback.feedback,
            comment=feedback.comment,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.execute(stmt)
        db.commit()
        return {"status": "Feedback saved successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect_anomalies")
async def api_detect_anomalies(
    host_id: str,
    time_period: int = 24
):
    """
    Detect anomalies for a host
    """
    try:
        zapi = connect_to_zabbix()
        host = zapi.host.get(hostids=[host_id], output=["host"])[0]
        items = zapi.item.get(
            hostids=[host_id],
            output=["itemid", "name"],
            monitored=True
        )

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_period)
        time_fmt = "%Y-%m-%d %H:%M"
        time_range = f"{start_time.strftime(time_fmt)} to {end_time.strftime(time_fmt)}"

        all_history = []
        for item in items[:20]:  # Limit to 20 items for performance
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

        return detect_anomalies(host["host"], time_range, all_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/root_cause_analysis")
async def api_root_cause_analysis(
    host_id: str,
    time_period: int = 24
):
    """
    Analyze the root cause of anomalies for a host
    """
    try:
        zapi = connect_to_zabbix()
        host = zapi.host.get(hostids=[host_id], output=["host"])[0]
        items = zapi.item.get(
            hostids=[host_id],
            output=["itemid", "name"],
            monitored=True
        )

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_period)
        time_fmt = "%Y-%m-%d %H:%M"
        time_range = f"{start_time.strftime(time_fmt)} to {end_time.strftime(time_fmt)}"

        all_history = []
        for item in items[:10]:  # Limit to 10 items for performance
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

        return analyze_root_cause(host["host"], time_range, all_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 