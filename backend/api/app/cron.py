from datetime import datetime, timedelta
from sqlalchemy import func
from app.db import db_session
from app.db.models import (
    Bovine, FeedingPatterns, FeedingAnalytics, SMSAlerts
)
from app.alerts import send_sms_alert

def parse_predictions(predictions):
    SILENCE_THRESHOLD_SECONDS = 300  # 5 minutes
    # predictions = list of (timestamp, label)
    sessions = []
    current_session = []
    last_time = None

    for timestamp, label in predictions:
        if label in ['chew', 'bite', 'chew-bite']:
            if last_time and (timestamp - last_time).total_seconds() > SILENCE_THRESHOLD_SECONDS:
                if current_session:
                    sessions.append(current_session)
                current_session = []
            current_session.append((timestamp, label))
            last_time = timestamp

    if current_session:
        sessions.append(current_session)
    return sessions

def calculate_metrics(predictions):
    sessions = parse_predictions(predictions)
    total_feeding_time = timedelta()
    feeding_frequencies = len(sessions)
    meal_durations = []
    feeding_rates = []
    total_chews_bites = len(predictions)

    for session in sessions:
        start = session[0][0]
        end = session[-1][0]
        duration = end - start
        duration_minutes = duration.total_seconds() / 60.0
        meal_durations.append(duration_minutes)
        total_feeding_time += duration

        num_chews = len(session)
        if duration_minutes > 0:
            feeding_rates.append(num_chews / duration_minutes)
        else:
            feeding_rates.append(0)

    # Metrics
    FT = total_feeding_time.total_seconds() / 60.0
    FF = feeding_frequencies
    MD = meal_durations
    AFT = FT / FF if FF > 0 else 0
    IMI = []
    for i in range(len(sessions) - 1):
        gap = (sessions[i+1][0][0] - sessions[i][-1][0])
        IMI.append(gap.total_seconds() / 3600.0)  # hours
    FR = feeding_rates
    TCPD = total_chews_bites

    return {
        "Feeding Time (FT)": FT,
        "Feeding Frequency (FF)": FF,
        "Meal Durations (MD)": MD,
        "Average Feeding Time (AFT)": AFT,
        "Inter-Meal Intervals (IMI)": IMI,
        "Feeding Rates (FR)": FR,
        "Total Chews/Bites Per Day": TCPD,
    }

def average(lst):
    return sum(lst) / len(lst) if lst else 0

def my_cron_job():
    print("Cron job executed", flush=True)
    db = db_session()
    try:
        today = datetime.utcnow().date()
        ten_days_ago = today - timedelta(days=10)

        bovines = db.query(Bovine).all()

        for bovine in bovines:
            bovine_id = bovine.id
            owner_id = bovine.owner_id

            # Get last 10 days of analytics (excluding today)
            past_analytics = db.query(FeedingAnalytics)\
                .filter(
                    FeedingAnalytics.bovine_id == bovine_id,
                    FeedingAnalytics.date >= ten_days_ago,
                    FeedingAnalytics.date < today
                ).all()

            if len(past_analytics) < 5:
                continue  # Not enough history for comparison

            # Get today's feeding patterns
            today_patterns = db.query(FeedingPatterns)\
                .filter(
                    FeedingPatterns.bovine_id == bovine_id,
                    func.date(FeedingPatterns.timestamp) == today
                ).all()

            if not today_patterns:
                continue

            label_map = {0: "chew", 1: "bite", 2: "chew-bite"}
            today_data = [(p.timestamp, label_map[p.bite_chew]) for p in today_patterns]
            today_metrics = calculate_metrics(today_data)

            # Extract today's scalar values
            today_vals = {
                "FT": today_metrics["Feeding Time (FT)"],
                "FF": today_metrics["Feeding Frequency (FF)"],
                "AFT": today_metrics["Average Feeding Time (AFT)"],
                "IMI": average(today_metrics["Inter-Meal Intervals (IMI)"]),
                "FR": average(today_metrics["Feeding Rates (FR)"]),
            }

            # Historical averages
            past_vals = {
                "FT": average([a.feeding_time.timestamp() / 60 for a in past_analytics]),
                "FF": average([a.feeding_frequency for a in past_analytics]),
                "AFT": average([a.average_feeding_time for a in past_analytics]),
                "IMI": average([a.meal_interval for a in past_analytics]),
                "FR": average([a.feeding_rate for a in past_analytics]),
            }

            def is_anomaly(metric, direction="decrease", threshold=0.3):
                t_val = today_vals[metric]
                p_val = past_vals[metric]
                if p_val == 0:
                    return False
                if direction == "decrease" and t_val < (1 - threshold) * p_val:
                    return True
                if direction == "increase" and t_val > (1 + threshold) * p_val:
                    return True
                return False

            anomalies = []
            if is_anomaly("FT", "decrease"):
                anomalies.append("Feeding Time ↓")
            if is_anomaly("FF", "decrease"):
                anomalies.append("Feeding Frequency ↓")
            if is_anomaly("AFT", "decrease"):
                anomalies.append("Avg. Feeding Time ↓")
            if is_anomaly("IMI", "increase"):
                anomalies.append("Meal Interval ↑")
            if is_anomaly("FR", "decrease"):
                anomalies.append("Feeding Rate ↓")

            if anomalies:
                message = f"ALERT! Bovine {bovine_id} feeding anomaly: " + ", ".join(anomalies)
                print(message, flush=True)

                send_sms_alert(message, bovine_id)
                db.add(SMSAlerts(
                    user_id=owner_id,
                    bovine_id=bovine_id,
                    timestamp=datetime.utcnow(),
                    message=message
                ))

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error in cron job: {e}", flush=True)
    finally:
        db.close()