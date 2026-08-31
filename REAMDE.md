# RecoverAI - Backend API

The core backend service for **RecoverAI**, built with **FastAPI**, **PostgreSQL**, and **Razorpay Webhooks**, integrated with a **Gemini AI Agent** to automate payment failure analysis and revenue recovery.

## 🚀 Key Features
* **Razorpay Integration:** Programmatically creates orders and handles secure webhook events (`payment.captured`, `payment.failed`).
* **Gemini AI Agent:** Automatically analyzes failure reasons and generates tailored customer recovery strategies, probability scores, and optimal communication channels.
* **Automated Recovery Execution:** Programmatically generates and dispatches Razorpay Payment Links for failed transactions.
* **Tenant Isolation:** Secure, multi-tenant merchant authentication using JWT tokens and PostgreSQL.

---

## 🛠️ Tech Stack
* **Python 3.10+ / FastAPI**
* **PostgreSQL / SQLAlchemy (Async)**
* **Razorpay Python SDK**
* **Google GenAI SDK (Gemini)**

---
