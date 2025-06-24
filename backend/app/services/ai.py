"""
AI service for anomaly detection and root cause analysis
"""
import google.generativeai as genai
import pandas as pd
import json

from ..core.config import GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


def call_gemini_api(prompt):
    """
    Call the Gemini API with a prompt
    """
    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(prompt)
    return response.text


def detect_anomalies(host_name, time_range, history_data):
    """
    Detect anomalies in the history data
    """
    # Convert history data to DataFrame for easier manipulation
    df = pd.DataFrame(history_data)
    
    # Create prompt for Gemini
    prompt = f"""
    Analyze the following monitoring data from Zabbix:

    Host: {host_name}
    Time: {time_range}
    Data:
    {df.to_string(index=False)}

    Return in JSON:
    {{
        "anomalies": [
            {{
                "metric": "...",
                "severity": "...",
                "cause": "...",
                "action": "..."
            }}
        ]
    }}
    """

    # Call Gemini API
    response_text = call_gemini_api(prompt)
    
    # Extract JSON from response
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    
    try:
        return json.loads(response_text[json_start:json_end])
    except json.JSONDecodeError:
        return {"anomalies": []}


def analyze_root_cause(host_name, time_range, history_data):
    """
    Analyze the root cause of anomalies
    """
    # Convert history data to DataFrame for easier manipulation
    df = pd.DataFrame(history_data)
    
    # Create prompt for Gemini
    prompt = f"""
    You are a monitoring expert. Below is Zabbix data:
    Host: {host_name}
    Time: {time_range}
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

    # Call Gemini API
    response_text = call_gemini_api(prompt)
    
    # Extract JSON from response
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    
    try:
        return json.loads(response_text[json_start:json_end])
    except json.JSONDecodeError:
        return {
            "root_cause": "Unable to determine",
            "evidence": [],
            "confidence": "Low",
            "recommendation": "Please check the system manually"
        } 