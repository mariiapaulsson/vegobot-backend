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
    msg = data.get("message")
    if not msg:
        return {"response": "Inget meddelande mottaget."}

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Du är en hjälpsam vego-assistent."},
                {"role": "user", "content": msg}
            ],
            temperature=0.7
        )
        return {"response": resp.choices[0].message.content.strip()}
    except Exception as e:
        return {"response": f"Något gick fel: {e}"}
