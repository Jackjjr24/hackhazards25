from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import init_database
from queries import get_response
from utils import generate_er_diagram
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

state = {
    "db": None,
    "db_uri": "",
    "db_type": ""
}

class DBConnectRequest(BaseModel):
    db_type: str
    user: str
    password: str
    host: str
    port: str
    database: str

@app.post("/api/connect")
def connect_db(req: DBConnectRequest):
    try:
        db, uri = init_database(req.db_type, req.user, req.password, req.host, req.port, req.database)
        state["db"] = db
        state["db_uri"] = uri
        state["db_type"] = req.db_type
        return {"message": "Connected successfully!"}
    except Exception as e:
        return {"message": f"Connection failed: {str(e)}"}

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
def query_db(req: QueryRequest):
    try:
        if not state["db"]:
            return {"response": "❌ Database not connected. Please connect first."}
        response = get_response(req.query, state["db"], [], state["db_type"])
        return {"response": response}
    except Exception as e:
        import traceback
        return {"response": f"Query failed:\n{traceback.format_exc()}"}

@app.get("/api/er-diagram")
def er_diagram():
    path = generate_er_diagram(state["db_uri"])
    return {"image_path": "/static/er_diagram.png"}
