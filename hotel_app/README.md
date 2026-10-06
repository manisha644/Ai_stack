# 🌴 Grand Palm Resort

A beginner-friendly Hotel Management & Booking website made with:

- Python
- Streamlit
- Ollama

## 1. Install Python

Use Python 3.10+ (your newer Python installation is recommended).

## 2. Install packages

Open PowerShell in this project folder:

```powershell
pip install streamlit ollama
```

If `pip` is not connected to your Python:

```powershell
python -m pip install streamlit ollama
```

## 3. Install Ollama

Install Ollama from the official Ollama website.

Then download the model:

```powershell
ollama pull llama3.2:3b
```

Make sure Ollama is running before using the AI Assistant page.

## 4. Run the website

```powershell
streamlit run app.py
```

The browser should open the Streamlit application.

## Project structure

hotel_app/
- app.py
- requirements.txt
- README.md

## Important

Bookings, reviews, cart items and chat messages are stored only in
Streamlit session state. They are temporary and are lost when the
session/server is restarted.
