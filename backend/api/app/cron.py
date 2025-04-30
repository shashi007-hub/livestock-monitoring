import datetime
from sqlalchemy import and_
from app.database.db import db_session
from app.database.models import FeedingAnalytics
from app.alerts import send_sms_alert
import numpy as np

def detect_anomalies(bovine_id, metrics_10_days):
    anomalies = []
    disease_map = {
        "Feeding Time (FT)": ("decrease", ["BRD", "metritis", "ketosis"]),
        "Feeding Frequency (FF)": ("decrease", ["BRD", "lameness", "stress"]),
        "Meal Durations (MD)": ("decrease", ["BRD", "fever", "pain"]),
        "Average Feeding Time (AFT)": ("decrease", ["BRD", "systemic inflammation"]),
        "Inter-Meal Intervals (IMI)": ("increase", ["BRD", "fatigue", "discomfort"]),
        "Feeding Rates (FR)": ("decrease", ["Oral pain", "illness"]),
        "Total Chews/Bites Per Day": ("decrease", ["BRD", "systemic illness"])
    }

    threshold = {
        "Feeding Time (FT)": 0.2,
        "Feeding Frequency (FF)": 0.2,
        "Meal Durations (MD)": 0.25,
        "Average Feeding Time (AFT)": 0.2,
        "Inter-Meal Intervals (IMI)": 0.3,
        "Feeding Rates (FR)": 0.25,
        "Total Chews/Bites Per Day": 0.25
    }

    # Separate baseline and recent days
    baseline_days = metrics_10_days[:7]
    recent_days = metrics_10_days[7:]

    for metric_name in threshold:
        try:
            baseline_vals = [day.metrics[metric_name] for day in baseline_days if metric_name in day.metrics]
            recent_vals = [day.metrics[metric_name] for day in recent_days if metric_name in day.metrics]
            if len(baseline_vals) < 3 or len(recent_vals) < 1:
                continue  # Not enough data
            baseline_avg = np.mean(baseline_vals)
            recent_avg = np.mean(recent_vals)
        except Exception:
            continue

        if baseline_avg == 0:
            continue  # Avoid divide-by-zero

        change = (recent_avg - baseline_avg) / baseline_avg
        direction, diseases = disease_map[metric_name]

        if direction == "decrease" and change < -threshold[metric_name]:
            anomalies.append({
                "metric": metric_name,
                "change": f"{change * 100:.1f}%",
                "diseases": diseases
            })
        elif direction == "increase" and change > threshold[metric_name]:
            anomalies.append({
                "metric": metric_name,
                "change": f"{change * 100:.1f}%",
                "diseases": diseases
            })

    return anomalies

def my_cron_job():
    print("Cron job executed", flush=True)
    db = db_session()
    try:
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=10)

        # Get distinct bovine IDs
        bovine_ids = db.query(FeedingAnalytics.bovine_id).distinct().all()
        bovine_ids = [b[0] for b in bovine_ids]

        for bovine_id in bovine_ids:
            records = db.query(FeedingAnalytics).filter(
                and_(
                    FeedingAnalytics.bovine_id == bovine_id,
                    FeedingAnalytics.date >= start_date,
                    FeedingAnalytics.date <= today
                )
            ).order_by(FeedingAnalytics.date.asc()).all()

            if len(records) < 10:
                print(f"Skipping bovine {bovine_id} due to insufficient data", flush=True)
                continue

            anomalies = detect_anomalies(bovine_id, records)
            if anomalies:
                msg = f"Anomalies detected for Bovine {bovine_id}:\n"
                for a in anomalies:
                    msg += f"- {a['metric']} changed by {a['change']} → possible: {', '.join(a['diseases'])}\n"
                send_sms_alert(msg, bovine_id)
                print(f"Alert sent for Bovine {bovine_id}", flush=True)
            else:
                print(f"No anomalies for Bovine {bovine_id}", flush=True)

    except Exception as e:
        print(f"Error during cron job: {e}", flush=True)
    finally:
        db.close()
