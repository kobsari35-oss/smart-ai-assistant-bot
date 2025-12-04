import os
import base64
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

def create_client():
    """
    បង្កើត OpenAI Client ដោយដោះស្រាយបញ្ហា Proxy (ប្រសិនបើមាន)
    """
    try:
        # រក្សាទុក Proxy settings បណ្ដោះអាសន្ន
        proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]
        saved = {k: os.environ.pop(k) for k in proxy_vars if k in os.environ}
        
        if not OPENAI_API_KEY: return None
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # ដាក់ Proxy ចូលវិញ
        os.environ.update(saved)
        return client
    except: return None

client = create_client()

def encode_image(image_path):
    """
    ប្លែងរូបភាពទៅជា Base64 string ដើម្បីផ្ញើទៅ AI
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def chatgpt_reply(prompt: str, image_path: str = None) -> str:
    """
    មុខងារហៅទៅ OpenAI (GPT-4o-mini)
    """
    if not client: return "⚠️ OpenAI API Key missing."
    try:
        # 🔥 System Prompt: កំណត់ចរិត AI ឱ្យឆ្លើយជាខ្មែរ និងចេះសង្ខេបបើវែងពេក
        system_content = (
            "You are a helpful AI assistant specialized in General Knowledge and Cambodian contexts. "
            "Reply in Khmer by default. "
            "If the user asks for a very long list (e.g., Law Articles 1-50), provide a summary "
            "or the first 5-10 items and ask if they want to read more, instead of refusing."
        )

        messages = [
            {"role": "system", "content": system_content},
        ]

        if image_path:
            # 🖼️ ករណីមានរូបភាព (Vision Mode)
            base64_image = encode_image(image_path)
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            })
            model = "gpt-4o-mini" # ឬ gpt-4o បើចង់បានច្បាស់ជាងនេះ
        else:
            # 💬 ករណីអក្សរសុទ្ធ (Text Mode)
            messages.append({"role": "user", "content": prompt})
            model = "gpt-4o-mini"

        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    except Exception as e: return f"⚠️ OpenAI Error: {e}"

def groq_reply(prompt: str) -> str:
    """
    មុខងារហៅទៅ Groq (Llama 3.3) - ប្រើពេល OpenAI មានបញ្ហា
    """
    if not GROQ_API_KEY: return "⚠️ GROQ not configured."
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        
        # System prompt សម្រាប់ Groq
        sys_msg = "You are a helpful assistant. Reply in Khmer."
        
        data = {
            "model": "llama-3.3-70b-versatile", 
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ]
        }
        
        res = requests.post(f"{GROQ_URL}/chat/completions", headers=headers, json=data, timeout=60)
        
        if res.status_code != 200:
            return f"⚠️ Groq Error: {res.text}"
            
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e: return f"⚠️ Groq Connection Error: {e}"

def smart_reply(prompt: str, image_path: str = None) -> str:
    """
    Main Function: សម្រេចចិត្តថាប្រើ AI មួយណា
    """
    # ១. បើមានរូបភាព ត្រូវតែប្រើ OpenAI (ព្រោះ Groq Free Tier មិនសូវស្គាល់រូប)
    if image_path:
        return chatgpt_reply(prompt, image_path)
    
    # ២. សាកប្រើ OpenAI មុន
    reply = chatgpt_reply(prompt)
    
    # ៣. បើ OpenAI Error ហើយយើងមាន Groq -> ប្រើ Groq ជំនួស
    if "Error" in reply and GROQ_API_KEY:
        return groq_reply(prompt)
        
    return reply