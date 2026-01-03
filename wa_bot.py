import os
import requests
import logging
from flask import Flask, request
from dotenv import load_dotenv
from openai import OpenAI
import io
from pypdf import PdfReader

# Load .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

# URL dasar API Telegram
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    """Fungsi untuk mengirim pesan balik ke Telegram"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def get_file_url(file_id):
    """Mendapatkan link download file dari Telegram"""
    # 1. Minta info file path
    r = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}")
    result = r.json()
    
    if result.get("ok"):
        file_path = result["result"]["file_path"]
        # 2. Buat URL download
        download_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        return download_url
    return None

@app.route('/bot', methods=['POST'])
def bot():
    # Telegram mengirim data dalam bentuk JSON
    update = request.get_json()
    
    # Pastikan ini pesan teks/dokumen (bukan status update)
    if "message" not in update:
        return "OK", 200

    message = update["message"]
    chat_id = message["chat"]["id"]
    
    # --- LOGIC 1: Handle Dokumen (PDF) ---
    if "document" in message:
        # Beritahu user sedang memproses
        send_message(chat_id, "📂 PDF diterima! Sedang membaca dan menganalisis...")
        
        file_id = message["document"]["file_id"]
        file_name = message["document"].get("file_name", "document.pdf")
        
        # Cek apakah PDF
        if not file_name.lower().endswith('.pdf'):
            send_message(chat_id, "❌ Harap kirim file format PDF.")
            return "OK", 200

        # Download dan Baca PDF
        try:
            download_url = get_file_url(file_id)
            if download_url:
                response = requests.get(download_url)
                pdf_file = io.BytesIO(response.content)
                reader = PdfReader(pdf_file)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text()
                
                # Kirim ke AI
                system_prompt = "Kamu adalah HRD expert. Analisis CV berikut dan berikan saran karir."
                user_content = f"Ini isi CV nya:\n{pdf_text[:4000]}" # Potong biar gak overload
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                reply = chat_completion.choices[0].message.content
                send_message(chat_id, reply)
            else:
                send_message(chat_id, "❌ Gagal mengambil file dari server Telegram.")
                
        except Exception as e:
            print(f"Error: {e}")
            send_message(chat_id, "❌ Terjadi error saat membaca PDF.")

    # --- LOGIC 2: Handle Text Biasa ---
    elif "text" in message:
        text_received = message["text"]
        
        # Kirim ke AI (Chat biasa)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Kamu asisten yang membantu."},
                {"role": "user", "content": text_received}
            ],
            model="llama-3.3-70b-versatile",
        )
        reply = chat_completion.choices[0].message.content
        send_message(chat_id, reply)

    return "OK", 200