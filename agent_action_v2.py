# -*- coding: utf-8 -*-
# agent_action_v2.py
# บอท 2: แผนกจัดการฐานข้อมูล Firebase (Database Agent)

import os
import datetime

# พยายามเชื่อมต่อ Firebase Firestore (มีโหมด Fallback อัตโนมัติ ป้องกันระบบล่ม)
db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # ตรวจสอบว่าเคยมีการ Initialize Firebase แล้วหรือไม่เพื่อป้องกัน Error ซ้ำซ้อน
    if not firebase_admin._apps:
        cred_path = "firebase-service-account.json"
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Successfully connected to Firebase Firestore!")
        else:
            print("firebase-service-account.json not found. Running in Local RAM mode.")
    else:
        db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}. Running in Local RAM mode.")

class DatabaseAgent:
    def __init__(self):
        self.name = "บอทฐานข้อมูล (บอท 2)"
        # ระบบจำลองฐานข้อมูลใน RAM ตัวเอง หากยังไม่ได้เชื่อมต่อ Firebase
        self.local_db = {}

    def save_note(self, session_id, content):
        """
        บันทึกข้อความลง Firebase Cloud Firestore 
        หากไม่เชื่อมต่อ จะเซฟลงตัวแปรดิบชั่วคราวบน RAM ให้ก่อน
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if db is not None:
            try:
                # บันทึกเป็นคอลเลกชันย่อยแยกตามผู้ใช้ (session_id)
                doc_ref = db.collection("users").document(session_id).collection("notes").document()
                doc_ref.set({
                    "content": content,
                    "timestamp": timestamp
                })
                return (f"🤖 [{self.name} ได้รับงานจากบอท 1]:\n"
                        f"✅ ดำเนินการจดบันทึกเรียบร้อยครับ!\n"
                        f"📝 ข้อความ: '{content}'\n"
                        f"☁️ บันทึกสำเร็จในระบบคลาวด์ Firebase Firestore")
            except Exception as e:
                return (f"🤖 [{self.name} ได้รับงานจากบอท 1 แต่เกิดข้อผิดพลาด]:\n"
                        f"❌ พยายามบันทึก '{content}' ลง Firebase แล้ว แต่ระบบแจ้งว่า: {str(e)}")
        else:
            # Fallback Mode: บันทึกเก็บใน RAM เครื่องชั่วคราว
            if session_id not in self.local_db:
                self.local_db[session_id] = []
            
            self.local_db[session_id].append({
                "content": content,
                "timestamp": timestamp
            })
            return (f"🤖 [{self.name} ได้รับงานจากบอท 1]:\n"
                    f"⚠️ (รันโหมดจำชั่วคราวเนื่องจากยังไม่ต่อ Firebase JSON)\n"
                    f"✅ บันทึกข้อความ: '{content}' สำเร็จ\n"
                    f"💾 จัดเก็บชั่วคราวไว้บนหน่วยความจำ RAM ของโฮสต์เรียบร้อยครับ!")

    def get_notes(self, session_id):
        """
        ดึงข้อมูลบันทึกทั้งหมดที่มีมาแสดงผล
        """
        if db is not None:
            try:
                notes_ref = db.collection("users").document(session_id).collection("notes")
                # ดึง 10 โน้ตล่าสุด เรียงลำดับตามเวลาล่าสุด
                docs = notes_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
                
                notes_list = []
                for doc in docs:
                    data = doc.to_dict()
                    notes_list.append(f"- {data['content']} (จดเมื่อ: {data['timestamp']})")
                
                if not notes_list:
                    return f"🤖 [{self.name}]: ค้นหาแล้ว ไม่พบข้อมูลการจดบันทึกของคุณใน Firebase เลยครับ"
                
                formatted_notes = "\n".join(notes_list)
                return (f"🤖 [{self.name} ดึงข้อมูลจากคลาวด์สำเร็จ]:\n"
                        f"📋 นี่คือประวัติบันทึก 10 รายการล่าสุดของคุณในระบบ Firebase:\n"
                        f"----------------------------------------\n"
                        f"{formatted_notes}")
            except Exception as e:
                return (f"🤖 [{self.name}]: ไม่สามารถดึงข้อมูลจากคลาวด์ Firebase ได้เนื่องจาก: {str(e)}")
        else:
            # ดึงข้อมูลจาก RAM
            notes = self.local_db.get(session_id, [])
            if not notes:
                return f"🤖 [{self.name}]: ค้นหาแล้ว ไม่พบข้อมูลบันทึกใดๆ ในหน่วยความจำชั่วคราว (RAM) เลยครับ"
            
            # เรียงจากล่าสุดขึ้นก่อน
            formatted_notes = "\n".join([f"- {n['content']} (จดเมื่อ: {n['timestamp']})" for n in reversed(notes)])
            return (f"🤖 [{self.name} ดึงข้อมูลชั่วคราวสำเร็จ]:\n"
                    f"📋 รายการบันทึกใน RAM (จะหายไปเมื่อแอปถูกสั่งรีสตาร์ต):\n"
                    f"----------------------------------------\n"
                    f"{formatted_notes}")
