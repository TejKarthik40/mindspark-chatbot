# Mental Health & Wellness Companion (Prototype)

## Overview
A local, offline-first prototype chatbot that:
- accepts text input (optionally plays TTS)
- detects mood (keyword + sentiment)
- recommends movies & music from local CSV
- saves a simple mood journal
- shows a wordcloud of recent entries

**Not a medical device.** For emergencies, contact professionals.

## Setup
1. Create virtualenv & activate.
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

## Notes
- First run may download a small transformers model for sentiment.
- TTS via `pyttsx3` is offline; ensure system dependencies available.
