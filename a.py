import os
import requests
import mysql.connector

# Vulnerability 1: Hardcoded API key
API_KEY = "sk_test_1234567890abcdef1234567890"

def get_weather(city):
    url = f"https://api.example.com/weather?city={city}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get(url, headers=headers, timeout=10).json()


# Vulnerability 2: SQL Injection
def get_user(cursor, username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    print("Sample created for static security analysis.")
