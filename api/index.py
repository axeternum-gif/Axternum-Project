from fastapi import FastAPI, HTTPException
from supabase import create_client
import os
from dotenv import load_dotenv

# Încărcăm variabilele (Vercel le injectează automat)
load_dotenv()

app = FastAPI()

# Conexiunea la Supabase (fosta linie 15)
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

@app.get("/")
def home():
    return {"status": "Axternum Engine Online", "univers": "Vercel"}

@app.get("/login")
def login(username: str, parola: str):
    # Logica de login (fosta linie 49)
    try:
        res = supabase.table('players').select("*").eq('username', username).eq('password', parola).execute()
        
        if len(res.data) > 0:
            return {"success": True, "player": res.data[0]}
        else:
            return {"success": False, "message": "Nume sau parola incorecta!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))