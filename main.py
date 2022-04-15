import os
from pathlib import Path
from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

MUSIC_FOLDER = Path(os.environ.get("MUSIC_FOLDER", "./files/"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory=MUSIC_FOLDER), name="media")
templates = Jinja2Templates(directory="templates")


@app.exception_handler(FileNotFoundError)
async def file_not_found_exception_handler(request, exc):
    raise HTTPException(status_code=404)


@app.get("/")
async def index():
    return RedirectResponse("/navigate/")


@app.get("/navigate/{directory_path:path}", response_class=HTMLResponse)
async def navigate(request: Request, directory_path: str):
    path = MUSIC_FOLDER.joinpath(directory_path)
    is_path_allowed = path == MUSIC_FOLDER or MUSIC_FOLDER in path.parents
    if not is_path_allowed:
        raise HTTPException(status_code=404)

    directory = list(os.scandir(path))
    return templates.TemplateResponse(
        "navigate.jinja2",
        {
            "request": request,
            "path": directory_path,
            "folders": [f.name for f in directory if f.is_dir()],
            "files": [
                {"name": f.name, "path": urljoin(directory_path, f.name)}
                for f in directory
                if f.is_file()
            ],
        },
    )
