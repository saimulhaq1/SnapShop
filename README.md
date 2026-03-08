# 🛒 SnapShop
**A Scalable, Production-Ready ML-Enhanced E-Commerce Platform**

SnapShop is a highly scalable, full-stack e-commerce solution built with Python. It leverages a strict MVC (Model-View-Controller) architecture and the robust Application Factory pattern to ensure maintainability, security, and high performance at scale.

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technical Stack](#-technical-stack)
4. [Deployment & Git Commands](#-deployment--git-commands)
5. [Docker Installation & Setup](#-docker-installation--setup)
6. [About the Developer](#-about-the-developer)

---

## 📸 Project Overview
![SnapShop Screenshot](https://github.com/saimulhaq1/SnapShop/blob/main/app/static/images/screenshot.png)

Designed as a modern e-commerce application, SnapShop demonstrates advanced architectural patterns and ML-readiness. It features an intelligent **Amazon-style interactive sidebar** dynamic filtering system that dynamically scopes category and parameter searches based on user interactions, offering an incredibly smooth UX.

---

## ✨ Key Features (Business Value & Engineering)
- **Advanced UI/UX Logic:** The frontend utilizes an Amazon-style interactive sidebar that processes dynamic, scalable parameter-based filtering logic.
- **Automated Deployment (CI/CD):** Fully containerized using Docker and configured with a robust GitHub Actions workflow to seamlessly build and push Docker containers to the GitHub Container Registry (GHCR) on every push.
- **Serverless PostgreSQL (Neon):** Production database managed flawlessly through Neon Serverless Postgres via an environment-injected `DATABASE_URL` string, automatically scaled to zero when idle.
- **Strict Architecture (MVC Application Factory):** Built with extreme decoupling through an MVC Application Factory structure, proving enterprise-grade codebase health.
- **Optimized Asset Delivery:** Utilizes `WhiteNoise` to efficiently serve static files (`/app/static/`) directly from the Python/WSGI layer.
- **ML/DL Ready:** The environment natively supports predictive analytics, recommendation algorithms, TensorFlow, and OpenCV Computer Vision processes right out of the box.

---

## 🛠 Technical Stack

### **Backend & Machine Learning**
![Python 3.11](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![Flask Factory / MVC](https://img.shields.io/badge/Flask%2FMVC-000000?style=for-the-badge&logo=flask&logoColor=white)
![Gunicorn & WhiteNoise](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)

### **Database**
![Neon Serverless Postgres](https://img.shields.io/badge/Neon_PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

### **DevOps & Deployment**
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

---

## 🐳 Docker Installation & Setup

To run this ML-Enhanced MVC application locally leveraging Docker, follow these instructions:

### 1. Configuration
Create a `.env` file in the root directory mirroring your database configurations or using your Neon Postgres string:
```env
FLASK_DEBUG=True
DATABASE_URL=postgresql://user:pass@ep-restless-bird.neon.tech/neondb?sslmode=require
```

### 2. Run with Docker Compose
Ensure you have Docker Desktop installed. The provided `docker-compose.yml` sets up a dedicated web service consuming your `.env` variables complete securely.

```bash
# Build the Docker image and start the Serverless Web Instance
docker-compose up --build
```
*The `curl`-based Docker healthcheck ensures the container strictly routes port 8000 successfully to localhost:5000.*

---

## 🚀 Deployment & Git Commands

To securely push this deployment-ready MVC architecture to your private GitHub repository and trigger the deployed GitHub Actions, run these exact terminal commands:

```bash
# 1. Clean up un-tracked directories and forcefully reset all staged/tracker files
git clean -fd
git restore --staged .

# 2. Add the clean MVC structure and production deployment files:
git add .

# 3. Commit your changes:
git commit -m "feat: Establish production MVC Application Factory with Neon Serverless DB, Docker Compose health checks, and GHCR deployment automation"

# 4. Push to your private repository (this triggers the Docker GHCR GitHub Action build!):
git push origin main
```

---

## 👨‍💻 About the Developer

**Hi, I'm Muhammad Saim Ulhaq!** 

I am a **Junior Python Developer based in Pakistan with 1+ years of experience**, specializing in **Machine Learning (ML) and Deep Learning (DL)**. I am deeply passionate about bridging the gap between complex AI models and real-world, scalable applications.

My core expertise lies in:
- Building, training, and optimizing **Neural Networks (ANNs, CNNs, RNNs)** for Computer Vision (OpenCV) and NLP.
- Designing highly scalable, strictly decoupled Python **MVC Application Factories**. 
- Automating infrastructure securely with **Docker Compose, GHCR Actions, and Serverless Databases**.

I leverage Python as my primary ecosystem to build robust backends that scale AI intelligent systems into consumer-ready platforms. 

📫 **Let's Connect!**
- **GitHub:** [github.com/saimulhaq1](https://github.com/saimulhaq1)

---
*SnapShop — Architected seamlessly by a passionate Python ML/DevOps Engineer.*
