#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 图像处理工具

提供图像处理功能
"""

from typing import Any, Union
from PIL import Image

from ..jm_entity import JmImageDetail
from ..jm_config import JmMagicConstants
from .text_tool import JmcomicText


class JmImageTool:
    """图像处理工具"""

    @classmethod
    def save_resp_img(cls, resp: Any, filepath: str, need_convert=True):
        """
        接收HTTP响应对象，将其保存到图片文件
        
        :param resp: JmImageResp
        :param filepath: 图片文件路径
        :param need_convert: 是否转换图片
        """
        if need_convert is False:
            cls.save_directly(resp, filepath)
        else:
            cls.save_image(cls.open_image(resp.content), filepath)

    @classmethod
    def save_image(cls, image: Image, filepath: str):
        """
        保存图片
        
        :param image: PIL.Image对象
        :param filepath: 保存文件路径
        """
        image.save(filepath)

    @classmethod
    def save_directly(cls, resp, filepath):
        from common import save_resp_content
        save_resp_content(resp, filepath)

    @classmethod
    def decode_and_save(cls, num: int, img_src: Image, decoded_save_path: str) -> None:
        """
        解密图片并保存
        
        :param num: 分割数
        :param img_src: 原始图片
        :param decoded_save_path: 解密图片的保存路径
        """
        if num == 0:
            cls.save_image(img_src, decoded_save_path)
            return

        import math
        w, h = img_src.size

        img_decode = Image.new("RGB", (w, h))
        over = h % num
        for i in range(num):
            move = math.floor(h / num)
            y_src = h - (move * (i + 1)) - over
            y_dst = move * i

            if i == 0:
                move += over
            else:
                y_dst += over

            img_decode.paste(
                img_src.crop((0, y_src, w, y_src + move)),
                (0, y_dst, w, y_dst + move)
            )

        cls.save_image(img_decode, decoded_save_path)

    @classmethod
    def open_image(cls, fp: Union[str, bytes]):
        from io import BytesIO
        fp = fp if isinstance(fp, str) else BytesIO(fp)
        return Image.open(fp)

    @classmethod
    def get_num(cls, scramble_id, aid, filename: str) -> int:
        """
        获得图片分割数
        """
        scramble_id = int(scramble_id)
        aid = int(aid)

        if aid < scramble_id:
            return 0
        elif aid < JmMagicConstants.SCRAMBLE_268850:
            return 10
        else:
            import hashlib
            x = 10 if aid < JmMagicConstants.SCRAMBLE_421926 else 8
            s = f"{aid}{filename}"
            s = s.encode()
            s = hashlib.md5(s).hexdigest()
            num = ord(s[-1])
            num %= x
            num = num * 2 + 2
            return num

    @classmethod
    def get_num_by_url(cls, scramble_id, url) -> int:
        """
        获得图片分割数
        """
        return cls.get_num(
            scramble_id,
            aid=JmcomicText.parse_to_jm_id(url),
            filename=url.split('/')[-1].split('.')[0],
        )

    @classmethod
    def get_num_by_detail(cls, detail: JmImageDetail) -> int:
        """
        获得图片分割数
        """
        return cls.get_num(detail.scramble_id, detail.aid, detail.img_file_name)
