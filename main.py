from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "API är igång"}

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    messages = data.get("messages")
    if not messages or not isinstance(messages, list):
        return {"response": "Ingen giltig konversation skickades."}

    # Mappa frontend roller till OpenAI-roller
    mapped_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        mapped_messages.append({"role": role, "content": msg["text"]})

    # Lägg till en system-prompt först
    system_prompt = {
        "role": "system",
        "content": (
            "Du är en hjälpsam vego-assistent som ger detaljerade och välstrukturerade "
            "receptförslag till köttälskare som vill äta mer vegetariskt. Svara alltid i snygg Markdown. "
            "Om användaren ställer en följdfråga (t.ex. 'kan jag byta ut tomat?') ska du föreslå alternativ "
            "som passar i just det specifika receptet istället för att börja ett nytt recept från början."
        )
    }

    full_messages = [system_prompt] + mapped_messages

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=full_messages,
            temperature=0.7
        )
        return {"response": resp.choices[0].message.content.strip()}
    except Exception as e:
        return {"response": f"Något gick fel: {e}"}
