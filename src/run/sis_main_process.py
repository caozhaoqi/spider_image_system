import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import sys
import uvicorn
from fastapi import FastAPI, applications
from loguru import logger
from src.log.log_base import LOG_DIR
from src.log.log_config import InterceptHandler, format_record
from src.router.router import api_router
from run.constants import app_port, sis_server_version, web_flag_start
from fastapi.openapi.docs import get_swagger_ui_html
from log.log_record import check_version


@logger.catch
def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.org/swagger-ui/4.15.5/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.org/swagger-ui/4.15.5/swagger-ui.min.css")


# Actual monkey patch
applications.get_swagger_ui_html = swagger_monkey_patch


@logger.catch
def init_app():
    """
    APP init : log router ...
    :return:
    """
    # fast api app 启动项配置与启动
    app = FastAPI(title="Spider Image System", version=sis_server_version,
                  description="API version", debug=True)
    # 路由引入
    app.include_router(router=api_router, prefix="/api/v1.0.1")
    # 日志配置与捕获
    logging.getLogger().handlers = [InterceptHandler()]
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}])
    logger.add(LOG_DIR, encoding='utf-8', rotation="00:00", retention="30 days", compression="zip")
    logger.debug('SIS log loaded, log path: ' + LOG_DIR)
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    return app


app = init_app()


@logger.catch
def api_main():
    """

    :return:
    """
    if not web_flag_start:
        check_version()
        uvicorn.run(app='sis_main_process:app', host='0.0.0.0', port=app_port, reload=False)
        logger.success("Web api starting!")
    else:
        logger.error("Web api already start!")


if __name__ == "__main__":
    api_main()
