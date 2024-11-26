import os
import sys
from pathlib import Path
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import uvicorn
from fastapi import FastAPI, applications
from loguru import logger
from log.log_base import LOG_DIR
from log.log_config import InterceptHandler, format_record
from router.router import api_router
from run.constants import sis_server_version, SpiderConfig
from fastapi.openapi.docs import get_swagger_ui_html
from log.log_record import check_version


def swagger_monkey_patch(*args: Any, **kwargs: Any) -> Any:
    """Customize Swagger UI assets with CDN versions
    
    Returns:
        HTML response with custom Swagger UI assets
    """
    return get_swagger_ui_html(
        *args, 
        **kwargs,
        swagger_js_url="https://cdn.staticfile.org/swagger-ui/4.15.5/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.org/swagger-ui/4.15.5/swagger-ui.min.css"
    )


# Apply monkey patch
applications.get_swagger_ui_html = swagger_monkey_patch


def init_logging() -> None:
    """Configure logging with loguru and file rotation"""
    logging.getLogger().handlers = [InterceptHandler()]
    logger.configure(handlers=[{
        "sink": sys.stdout,
        "level": logging.DEBUG,
        "format": format_record
    }])
    logger.add(
        LOG_DIR,
        encoding='utf-8',
        rotation="00:00",
        retention="30 days",
        compression="zip"
    )
    logger.debug(f'SIS log loaded, log path: {LOG_DIR}')
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]


def create_app() -> FastAPI:
    """Initialize and configure FastAPI application
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Spider Image System",
        version=sis_server_version,
        description="API version",
        debug=True
    )
    app.include_router(
        router=api_router,
        prefix=f"/api/{sis_server_version}"
    )
    init_logging()
    app.openapi_version = "3.0.0"
    return app


app = create_app()


def start_api_server() -> None:
    """Start the API server if not already running"""
    if not SpiderConfig.web_flag_start:
        check_version()
        uvicorn.run(
            app='sis_main_process:app',
            host='0.0.0.0',
            port=SpiderConfig.app_port,
            reload=False
        )
        logger.success("Web API started successfully!")
    else:
        logger.error("Web API is already running!")


if __name__ == "__main__":
    start_api_server()
