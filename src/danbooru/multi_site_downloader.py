#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path

# from src.data_pipeline.collectors.danbooru_spider import (
#     DanbooruMirrorSpider
# )


class MultiSiteDownloader:

    SITES = [
        "danbooru",
        "gelbooru",
        "safebooru",
        "konachan"
    ]

    def download_character(
        self,
        tag,
        output_dir,
        target_count=300
    ):

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        for site in self.SITES:

            print(
                f"\n[{site}] downloading..."
            )

            spider = DanbooruMirrorSpider(
                site=site,
                max_workers=16
            )

            spider.download_character_images(
                tag,
                str(output_dir),
                max_count=target_count
            )

            current = len(
                list(output_dir.glob("*"))
            )

            print(
                f"current images={current}"
            )

            if current >= target_count:
                break