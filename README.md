# 5ARE0 – Human Activity Recognition (HAR)
Assignment 1 for **5ARE0: Data Analysis and Learning Methods**: Human Activity Recognition for Healthy Lifestyle Monitoring.  
This folder contains all files to rerun the experiment and to see the results.  

## 🧪 Research Questions
1. Which sensor-based features best discriminate between activities?
2. How do supervised and unsupervised approaches compare?
3. Which model performs best on our dataset?
4. What are the limits for real-world deployment?

## 🔧 Environment
- **Python**: 3.11
- **Modules**:
   - pandas==2.3.2
   - numpy==2.3.3
   - scikit-learn==1.7.2
   - scipy==1.16.2
   - matplotlib==3.10.6
   - scikit-fuzzy==0.5.0
   - plotly==6.3.0
   - ipykernel==6.30.1

### Create & activate a virtual environment
```bash
python3 -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
````

### Install dependencies
```bash
pip install -r requirements.txt
```

## 📂 Data
Place the **Sensor Logger** exports (`.zip`) in `./data`.
Use the naming convention `action_x.zip`, where `action` is the activity and `x` is the anonymized participant number.


**Expected structure:**
```
./data
├── climbingStairs_x.zip
├── running_x.zip
├── sittingDown+StandingUp_x.zip
├── walking_x.zip
└── ......
```

## 🧠 Models Implemented
* **Supervised**: Logistic Regression, Decision Tree, Gaussian Naive Bayes, K-Nearest Neighbors
* **Unsupervised**: K-Means, Gaussian Mixture Model, Fuzzy C-Means (via `scikit-fuzzy`)
**Metrics reported**: Accuracy, Macro F1, Cohen’s Kappa.
**Visuals**: confusion matrices and metric bar charts per model/window size.

## 📁 Repository Structure
```
.
├── group13_activity_recognition.ipynb  # Jupyter notebook with all code
├── group13_Report.pdf                  # Report
├── data/                               # Directory for datasets
├── protocol.wav                        # Audio cues guiding the sit–down/stand–up recording
├── requirements.txt                    # List of Python dependencies
└── README.md                           # Project overview, setup, and usage
```

## 🔒 Ethics & Privacy
All participants gave consent. Data are anonymized and used solely for this course assignment.