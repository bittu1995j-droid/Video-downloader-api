from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fetch-video")
async def fetch_video(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True, 
        'format': 'best',
        'noplaylist': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'nothrow_on_empty_user_agent': True, 'concurrent_fragment_downloads': 10.    }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            download_links = []
            
            for f in formats:
                # Video + Audio (MP4) logic
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res:
                        download_links.append({"quality": f"{res}p", "ext": "mp4", "url": f.get('url')})
                # Audio logic
                elif f.get('vcodec') == 'none' and (f.get('ext') == 'm4a' or f.get('acodec') != 'none'):
                    download_links.append({"quality": "Audio (MP3)", "ext": "mp3", "url": f.get('url')})
            
            return {
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail', ''),
                "links": download_links
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
