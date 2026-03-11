import importlib
import logging
import os
import pkgutil
import traceback
from contextlib import asynccontextmanager
from datetime import datetime

#from core.config import settings
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

# MODULE_IMPORTS_START
from services.database import initialize_database, close_database
from services.mock_data import initialize_mock_data
from services.auth import initialize_admin_user
# MODULE_IMPORTS_END


def setup_logging():
    """Configure the logging system."""
    if os.environ.get("IS_LAMBDA") == "true":
        return

    # Create the logs directory
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/app_{timestamp}.log"

    # Configure log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure the root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            # File handler
            logging.FileHandler(log_file, encoding="utf-8"),
            # Console handler
            logging.StreamHandler(),
        ],
    )

    # Set log levels for specific modules
    logging.getLogger("uvicorn").setLevel(logging.DEBUG)
    logging.getLogger("fastapi").setLevel(logging.DEBUG)

    # Log configuration details
    logger = logging.getLogger(__name__)
    logger.info("=== Logging system initialized ===")
    logger.info(f"Log file: {log_file}")
    logger.info("Log level: INFO")
    logger.info(f"Timestamp: {timestamp}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger(__name__)
    logger.info("=== Application startup initiated ===")

    # MODULE_STARTUP_START
    await initialize_database()
    await initialize_mock_data()
    await initialize_admin_user()
    # MODULE_STARTUP_END

    logger.info("=== Application startup completed successfully ===")
    yield
    # MODULE_SHUTDOWN_START
    await close_database()
    # MODULE_SHUTDOWN_END


app = FastAPI(
    title="FastAPI Modular Template",
    description="A best-practice FastAPI template with modular architecture",
    version="1.0.0",
    lifespan=lifespan,
)


# MODULE_MIDDLEWARE_START
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
# MODULE_MIDDLEWARE_END


# Auto-discover and include all routers from the local `routers` package
def include_routers_from_package(app: FastAPI, package_name: str = "routers") -> None:
    """Discover and include all APIRouter objects from a package.

    This scans the given package (and subpackages) for module-level variables that
    are instances of FastAPI's APIRouter. It supports "router", "admin_router" names.
    """

    logger = logging.getLogger(__name__)

    try:
        pkg = importlib.import_module(package_name)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.debug("Routers package '%s' not loaded: %s", package_name, exc)
        return

    discovered: int = 0
    for _finder, module_name, is_pkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        # Only import leaf modules; subpackages will be walked automatically
        if is_pkg:
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to import module '%s': %s", module_name, exc)
            continue

        # Check for router variable names: router and admin_router
        for attr_name in ("router", "admin_router"):
            if not hasattr(module, attr_name):
                continue

            attr = getattr(module, attr_name)

            if isinstance(attr, APIRouter):
                app.include_router(attr)
                discovered += 1
                logger.info("Included router: %s.%s", module_name, attr_name)
            elif isinstance(attr, (list, tuple)):
                for idx, item in enumerate(attr):
                    if isinstance(item, APIRouter):
                        app.include_router(item)
                        discovered += 1
                        logger.info("Included router from list: %s.%s[%d]", module_name, attr_name, idx)

    if discovered == 0:
        logger.debug("No routers discovered in package '%s'", package_name)


# Setup logging before router discovery
setup_logging()
include_routers_from_package(app, "routers")


# Add exception handler for all exceptions except HTTPException
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions except HTTPException

    - Dev environment: Return full stack trace and exception details
    - Prod environment: Return only "Internal server error"
    """
    # Re-raise HTTPException to let FastAPI handle it normally
    if isinstance(exc, HTTPException):
        raise exc

    logger = logging.getLogger(__name__)
    error_message = str(exc)
    error_type = type(exc).__name__

    # Log full error details regardless of environment
    logger.error(f"Exception: {error_type}: {error_message}\n{traceback.format_exc()}")

    # Determine if we're in dev environment
    is_dev = os.getenv("ENVIRONMENT", "prod").lower() == "dev"

    if is_dev:
        # Dev environment: return full stack trace and exception details
        error_detail = f"{error_type}: {error_message}\n{traceback.format_exc()}"
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": error_detail})
    else:
        # Prod environment: return only generic error message
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"}
        )


@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>POデジタル秘書</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f5f7fb; margin:0; padding:30px; }
            .wrap { max-width:1000px; margin:0 auto; background:#fff; padding:24px; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,0.08); }
            h1 { color:#1f3c88; margin-top:0; }
            .grid { display:grid; grid-template-columns:repeat(2, 1fr); gap:16px; margin-top:20px; }
            a.card {
                display:block; text-decoration:none; background:#eef3ff; color:#1f3c88;
                padding:20px; border-radius:10px; font-size:20px; font-weight:bold;
            }
            p { color:#555; }
        </style>
    </head>
    <body>
        <div class="wrap">
            <h1>POデジタル秘書</h1>
            <p>営業・症例・見積・製作指示をつなぐ業務画面</p>

            <div class="grid">
                <a class="card" href="/sales">営業登録</a>
                <a class="card" href="/case">症例入力</a>
                <a class="card" href="/estimate">見積作成</a>
                <a class="card" href="/admin">管理画面</a>
            </div>
        </div>
    </body>
    </html>
    """"FastAPI Modular Template is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def run_in_debug_mode(app: FastAPI):
    """Run the FastAPI app in debug mode with proper asyncio handling.

    This function handles the special case of running in a debugger (PyCharm, VS Code, etc.)
    where asyncio is patched, causing conflicts with uvicorn's asyncio_run.

    It loads environment variables from ../.env and uses asyncio.run() directly
    to avoid uvicorn's asyncio_run conflicts.

    Args:
        app: The FastAPI application instance
    """
    import asyncio
    from pathlib import Path

    import uvicorn
    from dotenv import load_dotenv

    # Load environment variables from ../.env in debug mode
    # If `LOCAL_DEBUG=true` is set, then MetaGPT's `ProjectBuilder.build()` will generate the `.env` file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
        logger = logging.getLogger(__name__)
        logger.info(f"Loaded environment variables from {env_path}")

    # In debug mode, use asyncio.run() directly to avoid uvicorn's asyncio_run conflicts
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(settings.port),
        log_level="info",
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())


if __name__ == "__main__":
    import sys

    import uvicorn

    # Detect if running in debugger (PyCharm, VS Code, etc.)
    # Debuggers patch asyncio which conflicts with uvicorn's asyncio_run
    is_debugging = "pydevd" in sys.modules or (hasattr(sys, "gettrace") and sys.gettrace() is not None)

    if is_debugging:
        run_in_debug_mode(app)
    else:
        # Enable reload in normal mode
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(settings.port),
            reload_excludes=["**/*.py"],
        )
# --- Admin UI -------------------------------------------------

from fastapi.responses import HTMLResponse

@app.get("/admin", response_class=HTMLResponse)
async def admin_ui():
    return """
    <html>
    <head>
        <title>POデジタル秘書 管理画面</title>
        <style>
            body { font-family: Arial; background:#f4f6f8; padding:40px; }
            h1 { color:#333; }
            .card { background:white; padding:20px; margin:20px 0; border-radius:8px; }
            a { text-decoration:none; color:#2563eb; font-size:18px; }
        </style>
    </head>
    <body>
        <h1>POデジタル秘書 管理画面</h1>

        <div class="card">
            <a href="/cases">症例管理</a>
        </div>

        <div class="card">
            <a href="/estimates">見積管理</a>
        </div>

        <div class="card">
            <a href="/parts">部品マスター</a>
        </div>

        <div class="card">
            <a href="/products">装具マスター</a>
        </div>

    </body>
    </html>
    """
from fastapi.responses import HTMLResponse


@app.get("/sales", response_class=HTMLResponse)
async def sales_page():
    return """
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>案件登録 | POデジタル秘書</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f5f7fb; margin:0; padding:30px; }
            .wrap { max-width:900px; margin:0 auto; background:#fff; padding:24px; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,0.08); }
            h1 { margin-top:0; color:#1f3c88; }
            .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
            label { display:block; font-weight:bold; margin-bottom:6px; }
            input, select, textarea {
                width:100%; padding:10px; border:1px solid #d0d7e2; border-radius:8px; box-sizing:border-box;
            }
            .full { grid-column:1 / -1; }
            .actions { margin-top:24px; display:flex; gap:12px; }
            button, a.btn {
                background:#1f3c88; color:#fff; border:none; padding:12px 18px; border-radius:8px; text-decoration:none; cursor:pointer;
            }
            a.sub { color:#1f3c88; text-decoration:none; }
        </style>
    </head>
    <body>
        <div class="wrap">
            <p><a class="sub" href="/">← トップへ戻る</a></p>
            <h1>案件登録</h1>

            <div class="grid">
                <div>
                    <label>管理番号</label>
                    <input placeholder="例: PO-2026-0001">
                </div>
                <div>
                    <label>受付日</label>
                    <input type="date">
                </div>

                <div>
                    <label>担当営業</label>
                    <input placeholder="担当営業名">
                </div>
                <div>
                    <label>担当技術者</label>
                    <input placeholder="担当技術者名">
                </div>

                <div>
                    <label>医療機関名</label>
                    <input placeholder="病院名">
                </div>
                <div>
                    <label>医師名</label>
                    <input placeholder="医師名">
                </div>

                <div>
                    <label>区分</label>
                    <select>
                        <option>新規</option>
                        <option>再作</option>
                        <option>修理</option>
                    </select>
                </div>
                <div>
                    <label>左右</label>
                    <select>
                        <option>左</option>
                        <option>右</option>
                        <option>両側</option>
                    </select>
                </div>

                <div class="full">
                    <label>備考</label>
                    <textarea rows="4" placeholder="自由記載"></textarea>
                </div>
            </div>

            <div class="actions">
                <button>保存（仮）</button>
                <a class="btn" href="/case">症例入力へ進む</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/case", response_class=HTMLResponse)
async def case_page():
    return """
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>症例入力 | POデジタル秘書</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f5f7fb; margin:0; padding:30px; }
            .wrap { max-width:900px; margin:0 auto; background:#fff; padding:24px; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,0.08); }
            h1 { margin-top:0; color:#1f3c88; }
            .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
            label { display:block; font-weight:bold; margin-bottom:6px; }
            input, select, textarea {
                width:100%; padding:10px; border:1px solid #d0d7e2; border-radius:8px; box-sizing:border-box;
            }
            .full { grid-column:1 / -1; }
            .actions { margin-top:24px; display:flex; gap:12px; }
            button, a.btn {
                background:#1f3c88; color:#fff; border:none; padding:12px 18px; border-radius:8px; text-decoration:none; cursor:pointer;
            }
            a.sub { color:#1f3c88; text-decoration:none; }
        </style>
    </head>
    <body>
        <div class="wrap">
            <p><a class="sub" href="/">← トップへ戻る</a></p>
            <h1>症例入力</h1>

            <div class="grid">
                <div>
                    <label>疾患名</label>
                    <input placeholder="例: 脳卒中後片麻痺">
                </div>
                <div>
                    <label>診断名</label>
                    <input placeholder="診断名">
                </div>

                <div>
                    <label>麻痺の有無</label>
                    <select>
                        <option>あり</option>
                        <option>なし</option>
                    </select>
                </div>
                <div>
                    <label>拘縮の有無</label>
                    <select>
                        <option>あり</option>
                        <option>なし</option>
                    </select>
                </div>

                <div>
                    <label>左右</label>
                    <select>
                        <option>左</option>
                        <option>右</option>
                        <option>両側</option>
                    </select>
                </div>
                <div>
                    <label>採型 / 採寸</label>
                    <select>
                        <option>採型</option>
                        <option>採寸</option>
                    </select>
                </div>

                <div>
                    <label>使用目的</label>
                    <select>
                        <option>歩行安定</option>
                        <option>尖足予防</option>
                        <option>内反矯正</option>
                        <option>膝折れ防止</option>
                    </select>
                </div>
                <div>
                    <label>想定装具</label>
                    <select>
                        <option>短下肢装具</option>
                        <option>SHB</option>
                        <option>SLB</option>
                    </select>
                </div>

                <div class="full">
                    <label>特記事項</label>
                    <textarea rows="5" placeholder="症例の詳細、医師指示、注意点など"></textarea>
                </div>
            </div>

            <div class="actions">
                <button>保存（仮）</button>
                <a class="btn" href="/estimate">見積作成へ進む</a>
            </div>
        </div>
        @app.get("/estimate", response_class=HTMLResponse)
async def estimate_page():
    return """
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>見積作成 | POデジタル秘書</title>
        <style>
            body { font-family: Arial, sans-serif; background:#f5f7fb; margin:0; padding:30px; }
            .wrap { max-width:900px; margin:0 auto; background:#fff; padding:24px; border-radius:12px; box-shadow:0 4px 16px rgba(0,0,0,0.08); }
            h1 { margin-top:0; color:#1f3c88; }
            .grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
            label { display:block; font-weight:bold; margin-bottom:6px; }
            input, select {
                width:100%; padding:10px; border:1px solid #d0d7e2; border-radius:8px; box-sizing:border-box;
            }
            .full { grid-column:1 / -1; }
            .total { background:#eef3ff; padding:16px; border-radius:10px; margin-top:20px; }
            button {
                background:#1f3c88; color:white; border:none; padding:12px 18px; border-radius:8px;
            }
        </style>
    </head>
    <body>
        <div class="wrap">
            <h1>見積作成</h1>

            <div class="grid">
                <div>
                    <label>装具種類</label>
                    <select>
                        <option>短下肢装具</option>
                        <option>SHB</option>
                        <option>SLB</option>
                    </select>
                </div>

                <div>
                    <label>採型 / 採寸</label>
                    <select>
                        <option>採型</option>
                        <option>採寸</option>
                    </select>
                </div>

                <div>
                    <label>継手</label>
                    <input placeholder="継手名">
                </div>

                <div>
                    <label>支柱</label>
                    <input placeholder="支柱名">
                </div>

                <div>
                    <label>足部</label>
                    <input placeholder="足部">
                </div>

                <div>
                    <label>加算</label>
                    <input placeholder="加算項目">
                </div>
            </div>

            <div class="total">
                <p>基本価格: 0 円</p>
                <p>部品合計: 0 円</p>
                <p>加算合計: 0 円</p>
                <h3>見積総額: 0 円</h3>
            </div>

            <br>
            <button>見積保存（仮）</button>

        </div>
    </body>
    </html>
    """
    </body>
    </html>
    """
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>POデジタル秘書</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                background: #f5f7fb;
                color: #222;
            }
            .header {
                background: #1f3c88;
                color: white;
                padding: 24px;
            }
            .header h1 {
                margin: 0;
            }
            .container {
                max-width: 1000px;
                margin: 24px auto;
                padding: 0 16px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.08);
                text-decoration: none;
                color: inherit;
                border: 1px solid #e5e7eb;
            }
            .card h2 {
                margin-top: 0;
                color: #1f3c88;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>POデジタル秘書</h1>
            <p>営業・症例・見積・製作指示をつなぐ業務支援システム</p>
        </div>
        <div class="container">
            <div class="grid">
                <a class="card" href="/sales">
                    <h2>営業登録</h2>
                    <p>案件の基本情報を登録します。</p>
                </a>
                <a class="card" href="/case">
                    <h2>症例入力</h2>
                    <p>疾患・左右・採型/採寸などを入力します。</p>
                </a>
                <a class="card" href="/estimate">
                    <h2>見積作成</h2>
                    <p>装具・部品・加算をもとに見積を作成します。</p>
                </a>
                <a class="card" href="/admin">
                    <h2>管理画面</h2>
                    <p>管理用ページへ移動します。</p>
                </a>
            </div>
        </div>
    </body>
    </html>
    """
