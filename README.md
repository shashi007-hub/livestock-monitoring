## 🐄 **Empowering Farmers with Real-Time Cattle Health Monitoring**

In rural communities, farmers rely on livestock not just for income—but for survival.  
Yet most of them don’t have the tools to detect when cattle are stressed, sick, or in danger—until it’s too late. Manual monitoring is slow, error-prone, and frankly, not scalable.

We built **CattlePlus** to change that. It's a rugged, low-power IoT hub that uses smart sensors and local AI to monitor cattle health in real time—even with little to no internet.  
Designed for real-world use, CattlePlus focuses on what's *essential*: affordability, offline support, and actionable insights at the farm level.


---

## ✅ Our Solution
We provide smart, affordable, wearable sensor devices paired with local AI processing to monitor cattle and aquatic animal health. Our open-source system supports:

- Activity tracking & lameness detection  
- Bioacoustics-based stress detection  
- Cow identification & disease detection  
- Skin disease and bite/chew classification  
- SMS alerts and mobile app interface (Flutter)

This system works in offline/online modes using Raspberry Pi or E2E cloud nodes, ensuring inclusivity and scalability.

---

## 🧠 Technical Overview

- **Hybrid AI Deployment**: On Raspberry Pi Zero and cloud/VMs
- **Sensor Integration**: MEMS microphone, accelerometer, camera (wearables)
- **Communication**: MQTT via Mosquitto, SMS (Kannel/Gammu)
- **Backend**: FastAPI + PostgreSQL + TimescaleDB
- **Mobile Interface**: Flutter app (multilingual)
- **Architecture**: Master-slave mesh network, scalable and modular

---

## 🔧 Open-Source Technologies Used

### Machine Learning Models
- SVM, CNN – Lameness Detection  
- VGGNet (Transfer Learning) – Stress Detection  
- XGBoost – Bite & Chew Classification  
- YOLOv11 – Cow Identification  
- ViT – Disease Identification  

### Frameworks & Tools
- PyTorch, ONNX, FastAPI, Uvicorn  
- Flutter, Node-RED, Docker, BalenaOS  
- paho-mqtt, NATS, pyLoRa, Kannel, Gammu

---

## 🗂 Datasets

- [Lameness Detection (Accelerometer)](https://www.sciencedirect.com/science/article/pii/S0168169923008888) *(Request from authors)*
- [Cattle Disease (Images)](https://universe.roboflow.com/sliit-kuemd/cattle-diseases)
- [Bioacoustic Stress (Audio)](https://www.kaggle.com/datasets/lscadfacomufms/cattle-bioacoustic-dataset)
- [Bite & Chew Classification](https://dataverse.unr.edu.ar/dataset.xhtml?persistentId=doi:10.57715/UNR/T7SDAX)

---

## 🔮 Planned Enhancements

- Multilingual App Support  
- Oestrus Phase Detection  
- GPS & Heart Rate Integration  
- Digital Milk Yield Tracking  
- Modular plug-and-play sensor scalability

---

## 🌍 Deployment

- Deployed on **Raspberry Pi Zero**, **VMs**, and **E2E network nodes**
- Works with 2G networks and SMS for offline areas
- Mesh-based architecture for scalable farm sizes

---

## 💸 Sustainability & Business Model

- Hardware Cost: ₹3,000 (borne upfront by us)  
- Subscription: ₹400/month (includes device, AI, SMS, cloud)  
- Operational Cost: ₹100/month → ₹300 profit/user/month  
- Break-even: 10 months (or 5 with 50% govt. subsidy)  
- Aligned with: Rashtriya Gokul Mission, National Livestock Mission

---

## 📷 Case Study Snapshots

- Interviewing Farmers  
- Recording Cattle Audio  
- Testing Sensors  
- Lumpy Skin Disease Detection

> 📸 [View Images & Recordings](https://github.com/shashi007-hub/livestock-monitoring)

---

## 📦 Access & Demos

- **GitHub Repo**: [Livestock Monitoring](https://github.com/shashi007-hub/livestock-monitoring)  
- **Workbench Web App**: [Live Demo](http://164.52.194.74:8000/)  
- **Mobile App**: [Download from Drive](https://drive.google.com/drive/folders/12bX0ncqKzv1TpDrqnhcI4tGe6obPycIU?usp=sharing)

---

## 🤝 License
This project is fully open-source and encourages local adaptation and contributions for long-term community ownership.

---


