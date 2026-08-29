# agent_base.py
import logging

class BaseAgent:
    """
    คลาสแม่ (Base Class) สำหรับเอเจนต์ทุกตัวในระบบ
    หากในอนาคตมีเอเจนต์เพิ่มเป็น 100 ตัว ทุกตัวจะสืบทอด (Inherit) จากคลาสนี้
    เพื่อให้มีมาตรฐานและโครงสร้างการทำงานเหมือนกันทั้งหมด
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def can_handle(self, message: str, context: dict) -> bool:
        """
        ตรวจสอบว่าข้อความที่ผู้ใช้พิมพ์เข้ามา เอเจนต์ตัวนี้สามารถจัดการได้หรือไม่
        ส่งกลับเป็น True หากจัดการได้, False หากจัดการไม่ได้
        """
        raise NotImplementedError("เอเจนต์ทุกตัวต้องเขียนฟังก์ชัน can_handle ของตัวเอง")

    def process(self, message: str, context: dict) -> dict:
        """
        ฟังก์ชันประมวลผลคำสั่งจริงและส่งกลับผลลัพธ์
        ส่งกลับเป็น Dictionary เช่น {"response": "ข้อความตอบกลับ", "status": "success"}
        """
        raise NotImplementedError("เอเจนต์ทุกตัวต้องเขียนฟังก์ชัน process ของตัวเอง")


class AgentRegistry:
    """
    ระบบทะเบียนเอเจนต์ส่วนกลาง (Central Registry)
    ทำหน้าที่ลงทะเบียนและบริหารจัดการเอเจนต์ทั้งหมด (รองรับการขยายตัวได้เป็น 100+ เอเจนต์)
    """
    def __init__(self):
        self._agents = []

    def register(self, agent: BaseAgent):
        """ลงทะเบียนเอเจนต์ใหม่เข้ามาในระบบ"""
        if not isinstance(agent, BaseAgent):
            raise TypeError("เอเจนต์ที่ต้องการลงทะเบียนต้องสืบทอดมาจาก BaseAgent เท่านั้น")
        self._agents.append(agent)
        logging.info(f"ลงทะเบียนเอเจนต์สำเร็จ: {agent.name} ({agent.description})")

    def get_all_agents(self):
        """ดึงรายชื่อเอเจนต์ทั้งหมดในระบบ"""
        return self._agents

    def route_and_process(self, message: str, context: dict) -> dict:
        """
        รับข้อความจากผู้ใช้ แล้วคัดกรองหาเอเจนต์ที่เหมาะสมที่สุดเพื่อทำงาน
        """
        # หาเอเจนต์ที่พร้อมทำงานนี้
        for agent in self._agents:
            # ข้ามบอท 1 (Chat Router) เพื่อไม่ให้ลูปในการตรวจเงื่อนไขทั่วไป
            if agent.name == "Bot_1_Chat":
                continue
                
            if agent.can_handle(message, context):
                logging.info(f"ส่งงานต่อให้เอเจนต์: {agent.name}")
                result = agent.process(message, context)
                result["handled_by"] = agent.name
                return result

        # หากไม่มีบอทตัวไหนรับทำเลย จะส่งให้ Bot 1 (บอทแชตทั่วไป) จัดการตอบกลับ
        chat_agent = next((a for a in self._agents if a.name == "Bot_1_Chat"), None)
        if chat_agent:
            result = chat_agent.process(message, context)
            result["handled_by"] = chat_agent.name
            return result

        return {
            "response": "ขออภัยด้วยครับ ขณะนี้ระบบไม่มีเอเจนต์ตัวใดสามารถประมวลผลคำสั่งนี้ได้",
            "handled_by": "System_Fallback"
        }

# สร้างอินสแตนซ์ของ Registry ไว้ใช้งานร่วมกันทั่วทั้งโปรเจกต์
registry = AgentRegistry()
