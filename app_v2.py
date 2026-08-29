# -*- coding: utf-8 -*-
# app_v2.py
# ระบบเชื่อมต่อประสานงานเอเจนต์ (2-Agent Web Integration)

import os
from flask import Flask, request, jsonify, render_template_string
from agent_chat_v2 import ChatAgent
from agent_action_v2 import DatabaseAgent

app = Flask(__name__)

# ลงทะเบียนเริ่มต้นใช้งาน "บอท 2 ตัว" ของเรา
bot_1_chat = ChatAgent()
bot_2_db = DatabaseAgent()

# สกินหน้าเว็บแชตสำหรับการคุยตอบโต้ง่ายๆ
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2-Agent Chatbot System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 600px; height: 80vh; background: #ffffff; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
        .chat-header { background: #0084ff; color: #ffffff; padding: 15px 20px; text-align: center; }
        .chat-header h1 { font-size: 1.5rem; margin-bottom: 5px; }
        .chat-header p { font-size: 0.85rem; opacity: 0.9; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; background: #fcfcfc; }
        .message { margin-bottom: 15px; display: flex; flex-direction: column; }
        .message .sender-name { font-size: 0.75rem; color: #666; margin-bottom: 3px; font-weight: bold; }
        .message-bubble { padding: 10px 15px; border-radius: 15px; max-width: 80%; font-size: 0.95rem; line-height: 1.4; white-space: pre-line; }
        .message.user { align-items: flex-end; }
        .message.user .message-bubble { background: #0084ff; color: #ffffff; border-top-right-radius: 2px; }
        .message.bot { align-items: flex-start; }
        .message.bot .message-bubble { background: #e4e6eb; color: #333; border-top-left-radius: 2px; }
        .chat-input-area { padding: 15px; border-top: 1px solid #e4e6eb; display: flex; background: #ffffff; }
        .chat-input { flex: 1; padding: 12px; border: 1px solid #ccd0d5; border-radius: 25px; outline: none; font-size: 0.95rem; transition: border 0.2s; }
        .chat-input:focus { border-color: #0084ff; }
        .send-btn { background: #0084ff; color: white; border: none; padding: 0 20px; margin-left: 10px; border-radius: 25px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
        .send-btn:hover { background: #0066cc; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        <h1>🤖 ระบบทีมสหายบอท 2 ตัว</h1>
        <p>บอท 1 (ประสานงานพูดคุย) 🤝 บอท 2 (จัดการ Firebase DB)</p>
    </div>
    <div class="chat-messages" id="chat-messages">
        <div class="message bot">
            <span class="sender-name">บอท 1 (คุยทักทาย)</span>
            <div class="message-bubble">สวัสดีครับ! ยินดีต้อนรับเข้าสู่แชตบอททีมงาน 2 คนครับ!
            
            พิมพ์คำสั่งคุยกับเราได้เลย:
            💡 พิมพ์: <b>บันทึก [ข้อความที่ชอบ]</b> (เพื่อสั่งบอท 2 ให้บันทึกข้อมูล)
            📋 พิมพ์: <b>ดูบันทึก</b> (เพื่อให้บอท 2 ไปค้นข้อมูลเก่ามาแสดง)</div>
        </div>
    </div>
    <div class="chat-input-area">
        <input type="text" id="chat-input" class="chat-input" placeholder="ลองพิมพ์ว่า: บันทึก ไปซื้อของพรุ่งนี้ หรือ พิมพ์ ดูบันทึก..." onkeydown="if(event.key === 'Enter') sendMessage()">
        <button class="send-btn" onclick="sendMessage()">ส่ง</button>
    </div>
</div>

<script>
    function sendMessage() {
        const input = document.getElementById("chat-input");
        const messageText = input.value.trim();
        if (!messageText) return;

        const chatMessages = document.getElementById("chat-messages");

        // 1. เพิ่มข้อความฝั่งผู้ใช้ขึ้นจอแชต
        chatMessages.innerHTML += `
            <div class="message user">
                <span class="sender-name">คุณ</span>
                <div class="message-bubble">${messageText}</div>
            </div>
        `;
        
        input.value = "";
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 2. เรียกหลังบ้านเพื่อคุยกับระบบเอเจนต์
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: messageText,
                session_id: "user-123"  // สามารถปรับเปลี่ยน session_id ได้อิสระ
            })
        })
        .then(response => response.json())
        .then(data => {
            // คัดแยกว่าใครเป็นผู้ตอบ เพื่อความน่ารักและเข้าใจง่ายในการทำแบรนดิ้งบอท
            let sender = "บอท 1 (ผู้ประสานงาน)";
            if (data.reply.includes("บอทฐานข้อมูล") || data.reply.includes("บอท 2")) {
                sender = "บอท 2 (ฐานข้อมูล)";
            }

            chatMessages.innerHTML += `
                <div class="message bot">
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
                    <div class="message-bubble">เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์ครับ! กรุณาลองใหม่อีกครั้ง</div>
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
        return jsonify({"reply": "บอท 1: มีอะไรให้ผมและเพื่อนๆ บอทช่วยไหมครับ?"})

    # ส่งงานต่อให้ บอท 1 (บอทคุย) ประมวลผลและเรียกใช้ บอท 2 (บอทฐานข้อมูล) ในแบบเบื้องหลัง
    reply = bot_1_chat.response(user_message, session_id, bot_2_db)
    
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
