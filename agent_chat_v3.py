# -*- coding: utf-8 -*-
# agent_chat_v3.py
# บอท 1 (พูดคุย v3): ดึงบุคลิกและสไตล์คำพูดจาก Firebase หรือ Local RAM

import random

class ChatAgent:
    def __init__(self):
        self.name = "บอทวิเคราะห์ภาษา (บอท 1)"

    def response(self, user_message, session_id, db_agent):
        """
        ประสานงานพูดคุย ดึงบุคลิกภาพ และความรู้ที่เหมาะสมตามที่กำหนดไว้ใน Firebase
        """
        msg = user_message.strip()

        # 1. โหลดข้อมูลบุคลิกภาพปัจจุบันของผู้ใช้คนนี้จากฐานข้อมูล
        active_persona_id = db_agent.get_active_persona(session_id)
        persona_data = db_agent.get_persona_data(active_persona_id)
        
        bot_name = persona_data.get("name", "บอทธรรมดา")
        ending_style = persona_data.get("ending", "ครับ")
        greetings_list = persona_data.get("greetings", ["สวัสดีครับ"])

        # 2. ตรวจสอบเงื่อนไขคำสั่งเปลี่ยนบุคลิกบอท (เช่น "เปลี่ยนโหมด สุภาพ", "สลับร่าง กวนๆ")
        if "เปลี่ยนโหมด" in msg or "เปลี่ยนร่าง" in msg or "สลับโหมด" in msg:
            target_persona = "normal"
            mode_name = "ปกติ"
            
            if "สุภาพ" in msg or "gentle" in msg.lower():
                target_persona = "gentle"
                mode_name = "สุภาพแสนดี"
            elif "กวน" in msg or "funny" in msg.lower():
                target_persona = "funny"
                mode_name = "กวนประสาทชวนฮา"
            
            # อัปเดตการเลือกโหมดลง Firebase หรือ RAM
            db_agent.set_active_persona(session_id, target_persona)
            
            # ดึงข้อมูลร่างใหม่มาตอบกลับทันทีเพื่อเปลี่ยนสีสันการทักทาย
            new_persona = db_agent.get_persona_data(target_persona)
            return (f"✨ [ระบบประสานงาน]: เปลี่ยนร่างเป็น '{new_persona['name']}' เรียบร้อยแล้วครับ!\n"
                    f"💬 \"{random.choice(new_persona['greetings'])}\"")

        # 3. ส่งต่อให้ บอท 2 ทำงานเมื่อพบคำสั่งเขียน "บันทึก" หรือ "จด"
        if msg.startswith("บันทึก ") or msg.startswith("จด "):
            content = msg.replace("บันทึก ", "", 1).replace("จด ", "", 1)
            # ดึงคำตอบจากบอท 2 แล้วเติมสไตล์การลงท้ายของตัวตนปัจจุบัน
            reply_from_db = db_agent.save_note(session_id, content)
            return f"{reply_from_db}\n\n🤖 [{bot_name}]: ได้ลงมือบันทึกให้เรียบร้อยแล้ว {ending_style}"

        # 4. ส่งต่อให้ บอท 2 ดึงข้อมูลสมุดโน้ตประวัติ
        elif msg in ["ดูบันทึก", "อ่านบันทึก", "ประวัติ", "แสดงบันทึก"]:
            reply_from_db = db_agent.get_notes(session_id)
            return f"{reply_from_db}\n\n🤖 [{bot_name}]: ไปหยิบสมุดบันทึกมาให้แล้ว {ending_style}"

        # 5. ค้นหา "คลังความรู้ส่วนบุคคล" ในฐานข้อมูล (บอท 5 - ค้นหาความรู้ดัดแปลง)
        knowledge_reply = db_agent.search_knowledge(msg)
        if knowledge_reply:
            return f"📚 [{bot_name} - พบบทความรู้ในคลัง]:\n{knowledge_reply}\n\nหวังว่าข้อมูลนี้จะมีประโยชน์นะ{ending_style}"

        # 6. กรณีการคุยทักทายทั่วไป หรือพูดคุยไร้สาระ
        if any(keyword in msg for keyword in ["สวัสดี", "หวัดดี", "ดีจ้า", "hello", "hi"]):
            greeting = random.choice(greetings_list)
            return (f"🤖 [{bot_name}]: {greeting}\n\n"
                    f"💡 *คุณสามารถสั่งงานเปลี่ยนบุคลิกของผมและเพื่อนๆ ได้ด้วยคำสั่งดังนี้:*\n"
                    f"👉 พิมพ์ 'เปลี่ยนโหมด สุภาพ' -> แปลงร่างเป็นสุภาพอ่อนโยน\n"
                    f"👉 พิมพ์ 'เปลี่ยนโหมด กวนๆ' -> แปลงร่างเป็นตลกกวนโอ๊ย\n"
                    f"👉 พิมพ์ 'เปลี่ยนโหมด ปกติ' -> กลับคืนสู่ร่างปกติสุดเท่\n\n"
                    f"และสั่งจดบันทึกได้เหมือนเดิม เช่นพิมพ์ 'บันทึก ซักผ้าเย็นนี้' {ending_style}")

        # 7. คุยโต้ตอบทั่วไป แบบตามใจตัวตนบอท
        return (f"🤖 [{bot_name}]: ฉันได้รับข้อความว่า '{msg}' นะ\n"
                f"แต่ไม่พบในคำสั่งหรือคลังความรู้ปัจจุบันเลย "
                f"ถ้ามีเรื่องอะไรอยากให้บันทึกหรือช่วยหา พิมพ์สั่งมาได้เลยนะ{ending_style}")
