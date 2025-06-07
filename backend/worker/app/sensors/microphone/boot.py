# boot.py
import network
import time

SSID = "wdssw"
PASSWORD = "sxaoljmlxa"

def wifi_connect(ssid, password, max_retries=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    attempt = 0

    while not wlan.isconnected() and attempt < max_retries:
        print(f"📡 Attempting Wi-Fi connection ({attempt + 1})...")
        wlan.connect(ssid, password)
        timeout = 1 << attempt  # exponential backoff (2^attempt seconds)
        for _ in range(timeout):
            if wlan.isconnected():
                break
            time.sleep(1)
        attempt += 1

    if wlan.isconnected():
        print("Connected to Wi-Fi:", wlan.ifconfig()[0])
    else:
        raise RuntimeError("Failed to connect to Wi-Fi")

wifi_connect(SSID, PASSWORD)

from main import main
main()