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
    conversation = data.get("conversation", [])

    if not conversation or not isinstance(conversation, list):
        return {"response": "Ingen giltig konversation skickades."}

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Du är en hjälpsam vego-assistent som ger detaljerade, välstrukturerade vegetariska recept "
                    "för köttälskare som vill äta mer grönt. "
                    "Svara alltid i snygg **Markdown** med rubriker, punktlistor för ingredienser, numrerade steg och radbrytningar. "
                    "Använd gärna passande emojis för att göra svaret mer levande (🥦 🍅 🌱).\n\n"
                    "Om användaren ber om att ändra något i ett tidigare recept eller fråga (t.ex. 'utan tomat'), "
                    "ge korta, konkreta förslag på hur ingredienser kan bytas ut eller justeras utan att skriva hela receptet igen."
                )
            }
        ] + conversation

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        return {"response": resp.choices[0].message.content.strip()}
    except Exception as e:
        return {"response": f"Något gick fel: {e}"}
