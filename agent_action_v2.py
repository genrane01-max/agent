# -*- coding: utf-8 -*-
# agent_action_v3.py
# บอท 2 (ฐานข้อมูล v3): แผนกจัดการ Firebase & ทะเบียนบุคลิก/คลังความรู้

import os
import datetime

# เชื่อมต่อ Firebase Firestore (มีโหมด Fallback เพื่อความปลอดภัยสูงสุด)
db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    if not firebase_admin._apps:
        cred_path = "firebase-service-account.json"
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Successfully connected to Firebase Firestore (v3)!")
        else:
            print("firebase-service-account.json not found. Running in Local RAM mode.")
    else:
        db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}. Running in Local RAM mode.")

class DatabaseAgent:
    def __init__(self):
        self.name = "บอทฐานข้อมูล (บอท 2)"
        
        # 1. ฐานข้อมูลท้องถิ่นใน RAM (Fallback) สำหรับจำสถานะผู้ใช้
        self.local_user_states = {} # {session_id: {"active_persona": "gentle"}}
        self.local_notes = {}       # {session_id: [{"content": "...", "timestamp": "..."}]}
        
        # 2. คลังอุปนิสัยเริ่มต้น (Fallback Personas)
        self.fallback_personas = {
            "gentle": {
                "name": "บอทสุภาพแสนใจดี",
                "ending": "ครับผม ยินดีให้บริการเสมอครับ",
                "greetings": [
                    "สวัสดีครับคุณผู้ใช้ มีอะไรให้ผมรับใช้ในวันนี้ไหมครับ?",
                    "สวัสดีครับ! วันนี้อากาศดีจัง มีข้อมูลอะไรอยากให้ผมช่วยจดบันทึกไหมครับ?"
                ],
                "description": "เน้นพูดจาสุภาพ เรียบร้อย อ่อนหวาน มีครับผมทุกคำ"
            },
            "funny": {
                "name": "บอทกวนๆ ชวนฮา",
                "ending": "นะจ๊ะสหายรัก! ฮ่าๆๆๆ",
                "greetings": [
                    "โย่ว! ว่าไงเจ้ามนุษย์! วันนี้มีงานยากๆ มาให้ฉันทำอีกหรือเปล่า?",
                    "แฮ่! บอทกวนประสาทรายงานตัว! อยากจดอะไรพิมพ์มาได้เลยนะฮะ!"
                ],
                "description": "เน้นพูดเล่น เป็นกันเอง กวนประสาทเล็กน้อย แฝงความตลกขบขัน"
            },
            "normal": {
                "name": "บอทปกติแสนขยัน",
                "ending": "ครับ ยินดีช่วยเหลือครับ",
                "greetings": [
                    "สวัสดีครับ! มีอะไรให้ผมช่วยเหลือพิมพ์บอกได้เลยครับ",
                    "สวัสดีครับ! วันนี้ต้องการบันทึกข้อความหรือดูประวัติบันทึกดีครับ?"
                ],
                "description": "บอทผู้ช่วยมาตรฐาน ตอบคำถามชัดเจน ตรงประเด็น"
            }
        }

        # 3. คลังความรู้เฉพาะทางเริ่มต้น (Fallback Knowledge Base)
        self.fallback_knowledge = [
            {
                "keywords": ["ผู้สร้าง", "ใครสร้าง", "คนสร้าง", "creator"],
                "content": "บอทอัจฉริยะระบบนี้ถูกพัฒนาขึ้นโดย 'คุณ genrane01-max' เพื่อเป็นสหายบอทไร้ API ภายนอกที่ทำงานประสานงานกันได้แบบ 100% ครับ!"
            },
            {
                "keywords": ["firebase", "ไฟร์เบส", "ฐานข้อมูล"],
                "content": "Firebase Firestore คือฐานข้อมูล Cloud แบบ NoSQL ฟรีที่เราใช้จัดเก็บข้อมูลโน้ตและสถานะบุคลิกของบอท ทำให้ข้อมูลไม่หายไปไหนแม้ว่าเซิร์ฟเวอร์ Render จะรีสตาร์ตก็ตามครับ"
            },
            {
                "keywords": ["วิธีใช้งาน", "คู่มือ", "คำสั่ง", "ทำอะไรได้บ้าง"],
                "content": "คุณสามารถสั่งงานผมได้ดังนี้ครับ:\n1. 'เปลี่ยนโหมด [ชื่อโหมด]' (เช่น เปลี่ยนโหมด สุภาพ หรือ เปลี่ยนโหมด กวนๆ)\n2. 'บันทึก [เรื่องที่ต้องการจด]'\n3. 'ดูบันทึก'\n4. ถามคำถามทั่วไป เช่น ถามเกี่ยวกับผู้สร้าง หรือ Firebase"
            }
        ]

    # --- ฟังก์ชันจัดการ "สมุดบันทึก (Notes)" ---
    def save_note(self, session_id, content):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if db is not None:
            try:
                doc_ref = db.collection("users").document(session_id).collection("notes").document()
                doc_ref.set({
                    "content": content,
                    "timestamp": timestamp
                })
                return f"✅ บันทึกสำเร็จลงระบบคลาวด์ Firebase เรียบร้อยครับ!\n📝 เนื้อหา: '{content}'"
            except Exception as e:
                return f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {str(e)} (แต่บันทึกสำเร็จลง RAM ชั่วคราวให้แล้ว)"
        
        # Fallback to RAM
        if session_id not in self.local_notes:
            self.local_notes[session_id] = []
        self.local_notes[session_id].append({"content": content, "timestamp": timestamp})
        return f"⚠️ [โหมดสำรอง RAM] บันทึกข้อมูล: '{content}' สำเร็จแล้วครับ"

    def get_notes(self, session_id):
        if db is not None:
            try:
                notes_ref = db.collection("users").document(session_id).collection("notes")
                docs = notes_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
                notes_list = [f"- {doc.to_dict()['content']} (จดเมื่อ: {doc.to_dict()['timestamp']})" for doc in docs]
                if not notes_list:
                    return "📋 ไม่พบข้อมูลการบันทึกของคุณใน Firebase ค้นหาแล้วว่างเปล่าครับ"
                return "📋 รายการบันทึก 10 รายการล่าสุดบนคลาวด์:\n" + "\n".join(notes_list)
            except Exception as e:
                return f"❌ ไม่สามารถดึงข้อมูลจากคลาวด์ได้: {str(e)}"
        
        # Fallback to RAM
        notes = self.local_notes.get(session_id, [])
        if not notes:
            return "📋 ไม่พบข้อมูลการบันทึกใดๆ ในความจำชั่วคราว (RAM)"
        return "📋 รายการบันทึกชั่วคราวใน RAM:\n" + "\n".join([f"- {n['content']} (จดเมื่อ: {n['timestamp']})" for n in reversed(notes)])

    # --- ฟังก์ชันจัดการ "อุปนิสัยบอท (Personas)" ---
    def get_active_persona(self, session_id):
        """ ดึงข้อมูลไอดีอุปนิสัยที่ผู้ใช้กำลังเปิดใช้งานอยู่ """
        if db is not None:
            try:
                user_ref = db.collection("users").document(session_id).get()
                if user_ref.exists:
                    data = user_ref.to_dict()
                    return data.get("active_persona", "normal")
            except Exception as e:
                print(f"Error fetching active persona: {e}")
        
        # Fallback
        if session_id in self.local_user_states:
            return self.local_user_states[session_id].get("active_persona", "normal")
        return "normal"

    def set_active_persona(self, session_id, persona_id):
        """ ตั้งค่าเปลี่ยนอุปนิสัยการคุยของบอทลงฐานข้อมูล """
        if persona_id not in ["normal", "gentle", "funny"]:
            persona_id = "normal"
            
        if db is not None:
            try:
                db.collection("users").document(session_id).set({
                    "active_persona": persona_id
                }, merge=True)
                return True
            except Exception as e:
                print(f"Error setting persona in Firebase: {e}")
        
        # Fallback to RAM
        if session_id not in self.local_user_states:
            self.local_user_states[session_id] = {}
        self.local_user_states[session_id]["active_persona"] = persona_id
        return True

    def get_persona_data(self, persona_id):
        """ ดึงสไตล์คำพูดทั้งหมดของบุคลิกนั้นๆ """
        # ดึงจาก Firebase (ถ้าคุณแอดคอลเลกชัน personas ไว้)
        if db is not None:
            try:
                doc = db.collection("personas").document(persona_id).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                print(f"Error reading persona details from Firebase: {e}")
        
        # คืนค่าสไตล์เริ่มต้นที่เราเตรียมไว้ในตัวแปร fallback
        return self.fallback_personas.get(persona_id, self.fallback_personas["normal"])

    # --- ฟังก์ชันดึง "คลังความรู้เฉพาะทาง" ---
    def search_knowledge(self, user_message):
        """ ค้นหาความรู้จากคีย์เวิร์ดในข้อความ """
        msg = user_message.lower()
        
        # ค้นหาใน Firebase คอลเลกชัน knowledge_base (หากคุณสร้างไว้)
        if db is not None:
            try:
                docs = db.collection("knowledge_base").stream()
                for doc in docs:
                    data = doc.to_dict()
                    keywords = data.get("keywords", [])
                    # ถ้าพบคำสำคัญในประโยคของผู้ใช้ ให้ส่งคำตอบความรู้นั้นกลับ
                    if any(kw.lower() in msg for kw in keywords):
                        return data.get("content")
            except Exception as e:
                print(f"Error searching knowledge base on Firebase: {e}")

        # ดึงข้อมูลจากคลังความรู้สำรองในตัวแปร fallback
        for item in self.fallback_knowledge:
            if any(kw.lower() in msg for kw in item["keywords"]):
                return item["content"]
                
        return None
