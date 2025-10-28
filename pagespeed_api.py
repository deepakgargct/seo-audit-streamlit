import requests
import json

def get_pagespeed_data(url, api_key):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "strategy": "mobile"
    }
    r = requests.get(endpoint, params=params, timeout=20)
    data = r.json()

    try:
        metrics = data["lighthouseResult"]["audits"]
        return {
            "LCP": metrics.get("largest-contentful-paint", {}).get("numericValue"),
            "CLS": metrics.get("cumulative-layout-shift", {}).get("numericValue"),
            "TBT": metrics.get("total-blocking-time", {}).get("numericValue"),
            "Performance Score": data["lighthouseResult"]["categories"]["performance"]["score"]
        }
    except:
        return {}
