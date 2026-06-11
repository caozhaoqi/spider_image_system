# -*- coding: utf-8 -*-
"""生成B站Netscape格式Cookie文件"""
import os

COOKIE_STR = (
    "buvid3=6592C030-4422-EFA9-878C-1B9F8DA8E2FE24234infoc; "
    "b_nut=1770088324; "
    "_uuid=110D87B91-BE610-DF65-14F2-CD8D9C5E810F327582infoc; "
    "buvid_fp=5e11f8781deaa20bf08b0e0ed525df9c; "
    "home_feed_column=5; "
    "buvid4=5A077B87-08C4-AF75-F8A2-DD05C689CEFA29972-026020311-BChkT12H7lVdA/OGjQ8Xwg%3D%3D; "
    "CURRENT_QUALITY=0; "
    "rpdid=|(JmYkJ~|Rk0J'u~~||))JRm; "
    "CURRENT_FNVAL=4048; "
    "csrf_state=0780ea7a8f6c19e229d468abc8172833; "
    "bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODE0MTk0NjEsImlhdCI6MTc4MTE2MDIwMSwicGx0IjotMX0.wR3-7zvPvwU_pdOOSXeU6J6mKLaXkD0iJn8xQayXZyY; "
    "bili_ticket_expires=1781419401; "
    "SESSDATA=8cf9937b%2C1796712261%2C8d198%2A62CjDRUOnJZxbVXwkmifx4PXTQXjNs0rZ_mzNasWF8t2vfTNYdvLbCWExdfD_Ed0g6uPwSVlJkYm9JZlFnNWpIaEdWWnNTU1JFSU1HYUd6bDM4NFA2c2lYMlp1RG5kYllfVFhRLXd5QS1LOFU4c3VkOGlXVWVtTEFIcFhrS1hqMnNRdWQ5Vkk1cHZRIIEC; "
    "bili_jct=ad256a4f079dd62fa7606d13c1ec7800; "
    "DedeUserID=335112696; "
    "DedeUserID__ckMd5=e388e55bd03d61df; "
    "sid=hawf8oqs; "
    "theme-tip-show=SHOWED; "
    "browser_resolution=1470-150; "
    "b_lsid=3CCA64D9_19EB56CEA54"
)

cookies = {}
for item in COOKIE_STR.split(";"):
    item = item.strip()
    if "=" in item:
        k, v = item.split("=", 1)
        cookies[k.strip()] = v.strip()

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bilibili_cookies.txt")
with open(output_path, "w") as f:
    f.write("# Netscape HTTP Cookie File\n")
    f.write("# https://curl.haxx.se/docs/http-cookies.html\n\n")
    for name, value in cookies.items():
        f.write(f".bilibili.com\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")

print(f"Cookie文件已生成: {output_path} ({os.path.getsize(output_path)} bytes)")