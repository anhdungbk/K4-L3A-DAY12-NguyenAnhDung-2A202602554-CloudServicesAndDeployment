"""Giao diện chat độc lập với các endpoint checkpoint của bài lab."""

from __future__ import annotations

import json
import os
import random
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

load_dotenv()
router = APIRouter()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "~deepseek/deepseek-flash-latest"


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=12)


def _request_completion(messages: list[ChatMessage]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(503, "OPENROUTER_API_KEY is not configured on the server.")

    payload = json.dumps({
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        "messages": [message.model_dump() for message in messages],
        "max_tokens": 700,
        "temperature": 0.7,
    }).encode("utf-8")
    request = Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://day12-agent-n45n.onrender.com",
            "X-OpenRouter-Title": "Day 12 Chat",
        },
        method="POST",
    )
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=45, context=ssl_context) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("The response did not contain text.")
        return content.strip()
    except HTTPError as error:
        try:
            reason = json.loads(error.read().decode("utf-8")).get("error", {}).get("message")
        except (json.JSONDecodeError, UnicodeDecodeError):
            reason = None
        raise HTTPException(502, reason or "OpenRouter rejected the request.") from error
    except (URLError, TimeoutError) as error:
        raise HTTPException(502, "Could not reach OpenRouter.") from error
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(502, "OpenRouter returned an unexpected response.") from error


@router.post("/chat")
def chat(payload: ChatRequest):
    """Phản hồi demo cho giao diện, tách biệt hoàn toàn khỏi endpoint /ask của CP."""
    time.sleep(random.uniform(0, 2))
    return {"answer": "HIHI chưa có api key"}


@router.get("/", response_class=HTMLResponse)
def chat_page():
    return """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Day 12 Chat</title>
<style>
:root{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#0b1020;color:#edf2ff;display:grid;place-items:center}.dancer{position:fixed;top:0;width:max(0px,calc((100vw - 900px)/2));height:100vh;object-fit:fill;z-index:0}.dancer.left{left:0}.dancer.right{right:0;transform:scaleX(-1)}main{position:relative;z-index:1;width:min(900px,100%);height:min(760px,100vh);display:flex;flex-direction:column;background:#121a31}header{padding:20px 24px;border-bottom:1px solid #263252;font-weight:700;font-size:18px}header span{color:#9fb4ff;font-size:13px;font-weight:500;margin-left:8px}#messages{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:14px}.message{max-width:78%;padding:12px 15px;border-radius:16px;line-height:1.5;white-space:pre-wrap}.user{align-self:flex-end;background:#526ee8}.assistant{align-self:flex-start;background:#202b49}.thinking{color:#aebce9;font-style:italic}form{display:flex;gap:10px;padding:16px;border-top:1px solid #263252}textarea{flex:1;resize:none;min-height:48px;max-height:140px;padding:13px;border:1px solid #34446f;border-radius:12px;background:#0d1428;color:inherit;font:inherit}button{border:0;border-radius:12px;padding:0 20px;background:#6f8cff;color:#07102c;font:inherit;font-weight:700;cursor:pointer}button:disabled{opacity:.55;cursor:wait}@media(max-width:900px){.dancer{display:none}main{height:100vh}.message{max-width:90%}}
</style></head><body><img class="dancer left" src="https://usagif.com/wp-content/uploads/gify/39-anime-dance-girl-usagif.gif" alt=""><img class="dancer right" src="https://usagif.com/wp-content/uploads/gify/39-anime-dance-girl-usagif.gif" alt=""><main><header>Day 12 Chat <span>DeepSeek Flash via OpenRouter</span></header><section id="messages" aria-live="polite"><div class="message assistant">Xin chào! Bạn muốn hỏi gì?</div></section><form id="chat-form"><textarea id="prompt" placeholder="Nhập câu hỏi… (Enter để gửi, Shift+Enter để xuống dòng)" required></textarea><button id="send" type="submit">Gửi</button></form></main>
<script>
const messages=[],list=document.querySelector('#messages'),form=document.querySelector('#chat-form'),prompt=document.querySelector('#prompt'),send=document.querySelector('#send');
function add(role,content,thinking=false){const item=document.createElement('div');item.className=`message ${role}${thinking?' thinking':''}`;item.textContent=content;list.append(item);list.scrollTop=list.scrollHeight;return item}
async function submit(){const text=prompt.value.trim();if(!text||send.disabled)return;prompt.value='';send.disabled=true;prompt.disabled=true;messages.push({role:'user',content:text});add('user',text);const waiting=add('assistant','Thinking…',true);try{const response=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages})});const raw=await response.text();let data;try{data=JSON.parse(raw)}catch{throw new Error(`Máy chủ trả lỗi ${response.status}. Hãy thử lại.`)}if(!response.ok)throw new Error(data.detail||'Không thể nhận phản hồi.');waiting.remove();messages.push({role:'assistant',content:data.answer});add('assistant',data.answer)}catch(error){waiting.textContent=`Lỗi: ${error.message}`;waiting.classList.remove('thinking')}finally{send.disabled=false;prompt.disabled=false;prompt.focus()}}
form.addEventListener('submit',event=>{event.preventDefault();submit()});prompt.addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submit()}});
</script></body></html>"""
