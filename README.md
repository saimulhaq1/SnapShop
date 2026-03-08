# 🛒 SnapShop
**A Scalable, ML-Enhanced E-Commerce Platform**

SnapShop is a full-stack e-commerce solution built with Python. It leverages a strict MVC (Model-View-Controller) architecture and the Application Factory pattern for maintainability and performance.

---

## ✨ Key Features
- **Advanced UI/UX Logic:** Amazon-style interactive sidebar with dynamic parameter-based filtering.
- **Strict Architecture (MVC Application Factory):** Enterprise-grade decoupled codebase.
- **ML/DL Ready:** Natively supports TensorFlow, OpenCV, and predictive analytics.

---

## 🛠 Technical Stack

### **Backend & Machine Learning**
![Python 3.11](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![Flask Factory / MVC](https://img.shields.io/badge/Flask%2FMVC-000000?style=for-the-badge&logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)

### **Database**
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

---

## 💻 Local Installation & Setup

### Prerequisites
- Python 3.10+
- MySQL Server running locally
- A database named `ecommerce` created in MySQL

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/saimulhaq1/SnapShop.git
cd SnapShop

# Create and activate virtual environment
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
FLASK_DEBUG=True
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/ecommerce
```

### 3. Run the Application
```bash
python run.py
```
The app will be available at **http://127.0.0.1:5000**

---

## 🚀 Git Commands

```bash
# Clean untracked files
git clean -fd

# Stage, commit, and push
git add .
git commit -m "feat: SnapShop local MySQL setup"
git push origin main
```

---

## 👨‍💻 About the Developer

**Muhammad Saim Ulhaq**  
Junior Python Developer based in Pakistan with 1+ years of experience, specializing in **Machine Learning (ML) and Deep Learning (DL)**.

- Building and optimizing **Neural Networks (ANNs, CNNs, RNNs)** for Computer Vision and NLP.
- Designing scalable Python **MVC Application Factories**.
- Implementing relational database schemas with **MySQL**.

📫 **GitHub:** [github.com/saimulhaq1](https://github.com/saimulhaq1)

---
*SnapShop — Architected by a passionate Python ML Engineer.*
