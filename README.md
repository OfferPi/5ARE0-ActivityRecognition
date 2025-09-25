# 5ARE0-ActivityRecognition-
This repository contains Assignment 1 for 5ARE0: Human Activity Recognition for Healthy Lifestyle Monitoring.

## 🔧 Python Virtual Environment Setup

1. **Create a virtual environment**  
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the environment**
   ```bash
   source .venv/bin/activate   # Linux / macOS
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📂 Data  

All datasets recorded with the **Sensor Logger** app should be stored in the `data/` directory.  
Each file corresponds to a specific activity (e.g., *running*, *walking*, *climbing stairs*) followed by an index number to distinguish multiple recordings of the same activity.  

Structure of the `./data` directory:  

```
./data
├── climbingStairs_1.zip
├── climbingStairs_2.zip
├── climbingStairs_3.zip
├── running_1.zip
├── running_2.zip
├── running_3.zip
├── sittingDown+StandingUp_1.zip
├── sittingDown+StandingUp_2.zip
├── sittingDown+StandingUp_3.zip
├── walking_1.zip
├── walking_2.zip
└── walking_3.zip
```