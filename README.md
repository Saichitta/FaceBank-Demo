# FaceBank — An Agentic AI Banking Assistant for Elderly & Accessibility Users 🏦

FaceBank is an AI-driven banking assistant designed to simplify and secure digital banking for elderly and differently-abled users. It enables users to perform core banking tasks—like checking balances, sending money, and creating fixed deposits—through **natural conversation**, using **face recognition** for authentication and **speech/text interaction**.

---

## 🚀 Features

- **Face Recognition Login:** Securely authenticate users using real-time facial recognition (demo using OpenCV).  
- **Conversational Banking:** Chat or speak with the agent to perform banking actions.  
- **Transaction Management:** Check balance, view recent transactions, and perform simulated transfers.  
- **FD Advisory:** Suggests the best Fixed Deposit options based on available balance.  
- **Multi-agent AI:**  
  - **Auth Agent:** Handles login and authentication.  
  - **Transaction Agent:** Simulates banking actions.  
  - **Advisory Agent:** Provides personalized financial recommendations.  
  - **Learning Agent:** Observes usage patterns and proactively assists users.

---

## 🖥️ Demo

Check out the live Streamlit demo here: [FaceBank Demo](https://facebank-demo.streamlit.app/)

---

## 🧩 Tech Stack

**Frontend:** Streamlit (demo prototype)  
**Backend / AI:** Python, FastAPI, LangGraph, OpenAI / Groq LLMs  
**Face Recognition:** OpenCV (optionally Azure Face API)  
**Speech Layer:** Whisper + gTTS (speech-to-text & text-to-speech)  
**Data Storage:** JSON (dummy data for prototype)  
**Security:** On-device processing for sensitive biometric data  

> Note: The current version uses dummy data and local face recognition for demo purposes. Full integration with real banking APIs and secure databases will be added later.

---
