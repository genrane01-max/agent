# -*- coding: utf-8 -*-
# app_v3.py
# ระบบเชื่อมต่อประสานงานเอเจนต์อัจฉริยะแบบเปลี่ยนบุคลิกได้ (Dynamic Persona Chat System)

import os
from flask import Flask, request, jsonify, render_template_string
from agent_chat_v3 import ChatAgent
from agent_action_v3 import DatabaseAgent

app = Flask(__name__)

# เรียกใช้งานคู่หูเอเจนต์
bot_1_chat = ChatAgent()
bot_2_db = DatabaseAgent()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Multi-Persona Bot</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 650px; height: 85vh; background: #ffffff; border-radius: 16px; box-shadow: 0 12px 28px rgba(0,0,0,0.12); display: flex; flex-direction: column; overflow: hidden; }
        
        /* ส่วนหัวแชต */
        .chat-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 18px 20px; text-align: center; }
        .chat-header h1 { font-size: 1.6rem; margin-bottom: 5px; letter-spacing: 0.5px; }
        .chat-header p { font-size: 0.85rem; opacity: 0.9; }
        
        /* ปุ่มทางเลือกการเปลี่ยนร่างบอท (Persona Selector) */
        .persona-bar { display: flex; justify-content: space-around; background: #eef2f7; padding: 10px; border-bottom: 1px solid #e2e8f0; }
        .persona-btn { border: none; padding: 8px 14px; border-radius: 20px; cursor: pointer; font-size: 0.8rem; font-weight: bold; transition: all 0.2s; display: flex; align-items: center; gap: 5px; }
        .persona-btn.normal { background: #cbd5e1; color: #1e293b; }
        .persona-btn.gentle { background: #fbcfe8; color: #9d174d; }
        .persona-btn.funny { background: #fef08a; color: #854d0e; }
        .persona-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        
        /* ช่องแชต */
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; background: #fafbfc; }
        .message { margin-bottom: 15px; display: flex; flex-direction: column; }
        .message .sender-name { font-size: 0.75rem; color: #64748b; margin-bottom: 3px; font-weight: bold; }
        .message-bubble { padding: 12px 16px; border-radius: 18px; max-width: 85%; font-size: 0.95rem; line-height: 1.5; white-space: pre-line; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        
        .message.user { align-items: flex-end; }
        .message.user .message-bubble { background: #4f46e5; color: #ffffff; border-top-right-radius: 2px; }
        
        .message.bot { align-items: flex-start; }
        .message.bot .message-bubble { background: #e2e8f0; color: #1e293b; border-top-left-radius: 2px; }
        .message.system { align-items: center; margin: 10px 0; }
        .message.system .message-bubble { background: #fee2e2; color: #991b1b; border-radius: 10px; font-size: 0.8rem; text-align: center; max-width: 90%; }
        
        /* ส่วนพิมพ์ข้อความ */
        .chat-input-area { padding: 15px; border-top: 1px solid #e2e8f0; display: flex; background: #ffffff; align-items: center; }
        .chat-input { flex: 1; padding: 12px 20px; border: 1px solid #cbd5e1; border-radius: 30px; outline: none; font-size: 0.95rem; transition: border 0.2s; }
        .chat-input:focus { border-color: #4f46e5; }
        .send-btn { background: #4f46e5; color: white; border: none; padding: 0 24px; margin-left: 10px; height: 45px; border-radius: 30px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
        .send-btn:hover { background: #4338ca; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        <h1>🤖 ระบบบอทเปลี่ยนบุคลิกอัจฉริยะ</h1>
        <p>จัดสรรคำพูดและฐานความรู้จาก Firebase Firestore โดยตรง</p>
    </div>
    
    <!-- แถบด่วนเพื่อการทดสอบกดเปลี่ยนร่างบอทได้ทันที -->
    <div class="persona-bar">
        <button class="persona-btn normal" onclick="sendSystemMessage('เปลี่ยนโหมด ปกติ')">⚙️ โหมดบอทปกติ</button>
        <button class="persona-btn gentle" onclick="sendSystemMessage('เปลี่ยนโหมด สุภาพ')">🌸 โหมดบอทสุภาพ</button>
        <button class="persona-btn funny" onclick="sendSystemMessage('เปลี่ยนโหมด กวนๆ')">🍌 โหมดบอทกวนๆ</button>
    </div>
    
    <div class="chat-messages" id="chat-messages">
        <div class="message bot">
            <span class="sender-name">ระบบผู้จัดแจง</span>
            <div class="message-bubble">ยินดีต้อนรับครับสหาย! ตอนนี้ระบบ <b>"โหลดอุปนิสัยและคลังความรู้แบบ Dynamic"</b> เปิดทำงานพร้อมแล้วครับ!

ลองพิมพ์คุยกับบอท หรือเลือกกดเปลี่ยนร่างด้านบนได้เลย!
📌 พิมพ์ทักทาย: <b>สวัสดี</b> (เพื่อทดสอบอุปนิสัยปัจจุบัน)
📝 พิมพ์จด: <b>บันทึก ฝนตกหนักมากวันนี้</b>
📋 พิมพ์เปิดดู: <b>ดูบันทึก</b>
💡 ลองพิมพ์คำเหล่านี้เพื่อถามความรู้: <b>'ผู้สร้าง คือใคร'</b> หรือ <b>'ทำอะไรได้บ้าง'</b> หรือ <b>'Firebase'</b> ครับ!</div>
        </div>
    </div>
    
    <div class="chat-input-area">
        <input type="text" id="chat-input" class="chat-input" placeholder="พิมพ์ข้อความคุย หรือทดสอบเปลี่ยนโหมดได้เลย..." onkeydown="if(event.key === 'Enter') sendMessage()">
        <button class="send-btn" onclick="sendMessage()">ส่ง</button>
    </div>
</div>

<script>
    // สั่งงานระบบจำพวกคลิกปุ่มเปลี่ยนอุปนิสัย
    function sendSystemMessage(commandText) {
        document.getElementById("chat-input").value = commandText;
        sendMessage();
    }

    function sendMessage() {
        const input = document.getElementById("chat-input");
        const messageText = input.value.trim();
        if (!messageText) return;

        const chatMessages = document.getElementById("chat-messages");

        // 1. นำคำพูดผู้ใช้แสดงบนหน้าจอ
        chatMessages.innerHTML += `
            <div class="message user">
                <span class="sender-name">คุณ</span>
                <div class="message-bubble">${messageText}</div>
            </div>
        `;
        
        input.value = "";
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 2. เรียกเซิร์ฟเวอร์ Flask หลังบ้านเพื่อประมวลผล
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: messageText,
                session_id: "user-123"
            })
        })
        .then(response => response.json())
        .then(data => {
            // จับคู่แบรนดิ้งของบอทที่ตอบตามชื่ออ้างอิงในแชต
            let sender = "บอท 1 (ผู้ประสานงาน)";
            let bubbleClass = "bot";
            
            if (data.reply.includes("บอทสุภาพ")) {
                sender = "🌸 บอทสุภาพแสนดี";
            } else if (data.reply.includes("บอทกวน")) {
                sender = "🍌 บอทกวนประสาทชวนฮา";
            } else if (data.reply.includes("บอทปกติ")) {
                sender = "⚙️ บอทปกติแสนขยัน";
            } else if (data.reply.includes("✅ บันทึกสำเร็จ") || data.reply.includes("📋 รายการบันทึก")) {
                sender = "💾 บอทฐานข้อมูล (บอท 2)";
            }

            chatMessages.innerHTML += `
                <div class="message ${bubbleClass}">
                    <span class="sender-name">${sender}</span>
                    <div class="message-bubble">${data.reply}</div>
                </div>
            `;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => {
            chatMessages.innerHTML += `
                <div class="message bot">
                    <span class="sender-name">ระบบขัดข้อง</span>
                    <div class="message-bubble">เกิดปัญหาระบบหลุดการเชื่อมต่อกับเซิร์ฟเวอร์ครับ!</div>
                </div>
            `;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default-user")

    if not user_message:
        return jsonify({"reply": "กรุณาพิมพ์ข้อความเพื่อสนทนากับสหายบอทครับ"})

    # เรียกใช้ตัวส่งต่อของบอท 1 (ประสานงาน) โดยส่งฐานข้อมูล (บอท 2) เข้าไปประกอบ
    reply = bot_1_chat.response(user_message, session_id, bot_2_db)
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
