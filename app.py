import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# 1. ตั้งค่าการเชื่อมต่อ Firebase (หัวสมองของบอท)
# คุณต้องมีไฟล์ serviceAccountKey.json ที่ได้จาก Firebase Console อยู่ในโฟลเดอร์เดียวกัน
cred = credentials.Certificate("serviceAccountKey.json") 
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Advanced AI Bot Brain is Online</h1><p>Connected to Firebase Firestore</p>"

# 2. ฟังก์ชันโต้ตอบ (Brain Logic) เชื่อมต่อฐานข้อมูล
@app.route("/ask", methods=["POST"])
def ask_bot():
    data = request.get_json()
    user_query = data.get("question", "").lower() 

    try:
        # ค้นหาคำตอบจาก Firestore ใน Collection ชื่อ 'brain'
        doc_ref = db.collection("brain").document(user_query)
        doc = doc_ref.get()

        if doc.exists:
            bot_answer = doc.to_dict().get("answer")
        else:
            bot_answer = "ขออภัยครับ ข้อมูลส่วนนี้ยังไม่ได้ถูกบันทึกในหัวสมองของผม"
            
        return jsonify({"status": "success", "response": bot_answer})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    # ใช้ Port จาก Environment Variable ที่ Render กำหนดให้
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))