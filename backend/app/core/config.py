"""
Configuration settings loaded from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Zabbix Configuration
ZABBIX_URL = os.getenv("ZABBIX_URL", "http://172.16.0.142/zabbix")
ZABBIX_USER = os.getenv("ZABBIX_USER", "Admin")
ZABBIX_PASSWORD = os.getenv("ZABBIX_PASSWORD", "zabbix")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "172.16.0.91")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "DATA")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Khuongphuc123")
DB_NAME = os.getenv("DB_NAME", "zabbix_data")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCy4T4o301ih--BgVeYddIaXaUKwElAKmo")

# Backend Server
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# Database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 