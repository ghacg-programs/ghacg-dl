import random
import time

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from yarl import URL

from app.request_check import verify_request_source
from utils.config import get_config
from utils.openlist import sign as openlist_sign

router = APIRouter()


@router.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="https://ghacg.com", status_code=302)


@router.get("/d/{path:path}", dependencies=[Depends(verify_request_source)])
def redirect(path: str) -> RedirectResponse:
    cfg = get_config()
    expire = int(time.time()) + 86400
    sign_value = openlist_sign(f"/{path}", cfg.sign_token, expire)
    # 均摊负载
    base = URL(random.choice(cfg.fs_base))
    target = (base / path).with_query(sign=sign_value)

    response = RedirectResponse(url=str(target), status_code=302)
    # 防止Cloudflare缓存导致返回过期链接
    response.headers["Cache-Control"] = "no-store, private, max-age=0"
    response.headers["Cloudflare-CDN-Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
