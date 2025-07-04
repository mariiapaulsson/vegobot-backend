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

    # Mappa frontendroller till OpenAI-roller
    mapped_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        mapped_messages.append({"role": role, "content": msg["text"]})

    # Lägg till system-prompt först
    system_prompt = {
        "role": "system",
        "content": (
            "Du är en hjälpsam vego-assistent som ger detaljerade och välstrukturerade vegetariska recept "
            "och mattips, formaterat i snygg **Markdown** med rubriker, punktlistor och numrerade steg.\n\n"
            "✅ Om användaren ber om köttrecept eller ingredienser med kött: Svara artigt att det är utanför ditt område men föreslå en vegetarisk variant istället.\n"
            "Exempel: 'Det är lite utanför mitt område, men jag kan föreslå en god vegetarisk variant istället!'\n\n"
            "✅ Om användaren frågar om något helt orelaterat till mat eller recept: Förklara artigt att du är en vego-assistent och håll konversationen på ämnet.\n\n"
            "✅ Vid följdfrågor som 'kan jag byta ut tomat?' ska du föreslå passande alternativ utan att börja om receptet.\n\n"
            "✅ Använd **snygg Markdown**:\n"
            "- Rubriker (#, ##, etc.)\n"
            "- Punktlistor för ingredienser\n"
            "- Numrerade steg för instruktioner\n"
            "- Emojis sparsamt men passande 🍆🥦🌱\n\n"
            "✅ Var alltid vänlig och inbjudande i tonen."
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
