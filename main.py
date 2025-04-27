import asyncio
import sqlite3
from fastapi import FastAPI, Body, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


DATABASE_NAME = "url_shortener.db"
with sqlite3.connect(DATABASE_NAME) as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_id TEXT NOT NULL UNIQUE,
            original_url TEXT NOT NULL
        )
    ''')

@app.post("/", status_code=status.HTTP_201_CREATED)
async def shorten_url(request: Request, url: str = Body(..., media_type="text/plain")):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT seq FROM sqlite_sequence WHERE name="urls"')
        last_id = cursor.fetchone()
        current_id = (last_id[0] + 1) if last_id else 1
        short_id = str(uuid.uuid4())[:7]

        try:
            cursor.execute(
                'INSERT INTO urls (short_id, original_url) VALUES (?, ?)',
                (short_id, url)
            )
        except sqlite3.IntegrityError:
            current_id += 1
            short_id = uuid.uuid4()[:7]
            cursor.execute(
                'INSERT INTO urls (short_id, original_url) VALUES (?, ?)',
                (short_id, url)
            )

        base_url = str(request.base_url).rstrip('/')
        print(short_id)
        return {"shortened_url": f"{base_url}/{short_id}"}


@app.get("/{short_id}")
async def redirect_to_original(short_id: str):
    print(short_id)
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT original_url FROM urls WHERE short_id = ?',
            (short_id,)
        )
        result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Short URL not found")
    print(result[0])
    return RedirectResponse(result[0], status_code=307)

# docker run -d -p 8080:8080 -v ./data:/app --name shortener url-shortener