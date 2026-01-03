import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pypdf import PdfReader
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

# ==========================================
# 🔑 BAGIAN INI WAJIB DIISI DENGAN KUNCI KAMU
# ==========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")

# ==========================================

# Setup Client Groq (Kita pakai Llama 3.3 biar pinter)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

# Memory Sementara (Menyimpan teks PDF per Nomor HP User)
# Format: {'+62812xxx': 'isi teks pdf...'}
user_data = {}

def get_pdf_text(pdf_url):
    """Download PDF dari Server Twilio & Ambil Teksnya"""
    print(f"📥 Mendownload PDF dari: {pdf_url}")
    try:
        # Twilio butuh username(SID) & password(Auth) buat download file media
        response = requests.get(pdf_url, auth=(TWILIO_SID, TWILIO_AUTH))
        
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"❌ Error baca PDF: {e}")
        return None

def ask_groq(question, context):
    """Kirim pertanyaan + konteks PDF ke AI"""
    print("🤖 Sedang tanya Groq...")
    
    # Prompt Engineering: Gabungkan Data PDF + Pertanyaan User
    prompt = f"""
    Kamu adalah asisten pintar. Jawab pertanyaan user berdasarkan dokumen berikut.
    
    ISI DOKUMEN:
    {context[:15000]} 
    (Catatan: Teks dipotong jika terlalu panjang)
    
    PERTANYAAN USER: {question}
    
    Jawab dengan bahasa Indonesia yang luwes dan jelas maksimal 1200 karakter.
    """
    
    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Model terbaru & terpintar di Groq
            messages=[{"role": "user", "content": prompt}]
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Maaf, AI lagi pusing: {e}"

@app.route("/bot", methods=['POST'])
def bot():
    # 1. Tangkap data dari pesan masuk WhatsApp
    incoming_msg = request.values.get('Body', '').lower()
    sender_number = request.values.get('From')
    num_media = int(request.values.get('NumMedia', 0)) # Cek ada file gak?
    
    resp = MessagingResponse()
    msg = resp.message()

    # --- SKENARIO A: User Mengirim FILE (PDF) ---
    if num_media > 0:
        media_type = request.values.get('MediaContentType0')
        
        # Pastikan yang dikirim adalah PDF
        if 'pdf' in media_type:
            pdf_url = request.values.get('MediaUrl0')
            msg.body("📂 PDF diterima! Tunggu bentar ya, lagi dibaca...")
            
            # Proses Ekstrak
            extracted_text = get_pdf_text(pdf_url)
            
            if extracted_text:
                # Simpan ke Memory Server
                user_data[sender_number] = extracted_text
                msg.body("✅ Sip! PDF sudah masuk otak saya. Silakan tanya apa aja tentang isinya.")
            else:
                msg.body("❌ Gagal baca PDF. Pastikan filenya tidak rusak/password.")
        else:
            msg.body("Maaf kak, tolong kirim file format PDF ya. Gambar belum bisa.")

    # --- SKENARIO B: User Mengirim TEKS (Chat Biasa) ---
    else:
        # Cek: User ini udah pernah setor PDF belum?
        if sender_number in user_data:
            # Kalau sudah ada PDF, jawab pakai RAG Groq
            jawaban = ask_groq(incoming_msg, user_data[sender_number])
            msg.body(jawaban)
        else:
            # Kalau belum ada PDF
            if "halo" in incoming_msg or "hi" in incoming_msg:
                 msg.body("Halo! 👋 Saya Bot Pembaca PDF. Silakan kirim file PDF dulu ke sini, nanti kita ngobrol.")
            else:
                 msg.body("Belum ada dokumen yang dibaca nih. Kirim file PDF dulu ya! 📄")
    
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)