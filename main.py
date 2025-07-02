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
    history = data.get("history", [])
    msg = data.get("message")
    
    if not msg:
        return {"response": "Inget meddelande mottaget."}

    # Gör om history till korrekt format
    formatted_history = []
    for item in history:
        role = "user" if item["role"] == "user" else "assistant"
        formatted_history.append({"role": role, "content": item["text"]})

    # Lägg till senaste frågan
    formatted_history.append({"role": "user", "content": msg})

    # Lägg till systemprompt först
    system_prompt = (
        "Du är en hjälpsam vego-assistent som ger detaljerade och välstrukturerade recept "
        "för köttälskare som vill äta mer vegetariskt.\n\n"
        "Svara alltid i **Markdown** med:\n"
        "- **Rubriker**\n"
        "- Punktlistor för ingredienser\n"
        "- Numrerade steg\n"
        "- Korta och tydliga instruktioner.\n"
        "Följ samtalet så att du kan svara på följdfrågor om samma recept."
    )
    formatted_history = [{"role": "system", "content": system_prompt}] + formatted_history

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=formatted_history,
            temperature=0.7
        )
        return {"response": resp.choices[0].message.content.strip()}
    except Exception as e:
        return {"response": f"Något gick fel: {e}"}
