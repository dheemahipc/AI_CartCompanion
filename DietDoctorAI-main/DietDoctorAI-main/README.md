# 🥗 DietDoctor AI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-Enabled-orange.svg)]()
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Homelab-326ce5.svg?logo=kubernetes)](https://kubernetes.io/)
[![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-ef7b4d.svg?logo=argo)](https://argoproj.github.io/cd/)

DietDoctor AI is a production-grade, conversational AI agent designed to act as a personalized dietician and health coach. Accessible entirely via WhatsApp, it leverages Google's Agent Development Kit (ADK) and the Gemini 2.5 Flash model to provide scientifically accurate diet and exercise plans. 

This project goes beyond a simple LLM wrapper by integrating custom Python math tools for accurate macronutrient calculations and utilizing a robust, zero-downtime GitOps deployment pipeline.

---

## ✨ Key Features

* **Accessible via WhatsApp:** Users interact naturally via WhatsApp; no app downloads or web interfaces required.
* **Intelligent Middleware (n8n):** Handles webhooks, filters for text-only inputs to prevent crashes, and triggers parallel "typing..." indicators for a seamless user experience.
* **Agentic Precision:** The AI is strictly prompt-engineered to stay within health/fitness domains and relies on explicit Python functions to calculate exact BMI, BMR (Mifflin-St Jeor), and macro targets, eliminating LLM math hallucinations.
* **GitOps CI/CD:** Fully automated deployments. Code pushes trigger GitHub Actions to build and tag new Docker images, which are then synced and deployed via ArgoCD with zero downtime.
* **Kubernetes Ready:** Engineered to run smoothly on Kubernetes clusters with proper health checks and fast APIs.

---

## 🏗️ System Architecture

The system is broken down into two main domains: the **Runtime Data Flow** and the **Deployment Pipeline**.

### 1. Runtime Data Flow
1. **User Input:** A user sends a text message to the WhatsApp Business number.
2. **n8n Orchestration:** n8n catches the webhook, filters out non-text media, and splits the flow:
   * *Branch A:* Sends an HTTP request to WhatsApp to display a "typing..." indicator.
   * *Branch B:* Sends an HTTP POST request with the user's message to the FastAPI backend.
3. **Agentic Core:** FastAPI manages the user session and passes the context to the Google ADK runner.
4. **Calculations:** The Gemini model communicates with custom Python `health_utils.py` tools to perform accurate health math.
5. **Delivery:** The final, formatted diet/exercise plan is returned to n8n and forwarded to the user's WhatsApp.

### 2. GitOps Deployment Pipeline
1. **Source of Truth:** Code is pushed to the `main` branch of this repository.
2. **Continuous Integration:** GitHub Actions builds a new Docker container, tags it with the latest version, and pushes it to a container registry.
3. **Continuous Deployment:** ArgoCD detects the new image tag, gracefully spins down the old Kubernetes pod, and brings up the new pod, ensuring uninterrupted service.

---

## 🛠️ Technology Stack

* **AI & Backend:** Python, FastAPI, Google Agent Development Kit (ADK), Google Gemini 2.5 Flash.
* **Calculations:** Native Python (Math isolation for LLM accuracy).
* **Middleware:** n8n, WhatsApp Business Cloud API.
* **DevOps & Infra:** Docker, GitHub Actions, ArgoCD, Kubernetes.

---
<img width="1554" height="1550" alt="image" src="https://github.com/user-attachments/assets/12c406db-a0f7-45d9-9a28-b46a5707ff95" />


<img width="1448" height="834" alt="image" src="https://github.com/user-attachments/assets/08902ffb-de9a-48d9-957c-4a0de517f299" />
