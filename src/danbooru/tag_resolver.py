#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from loguru import logger


class DanbooruTagResolver:

    API_URL = "https://danbooru.donmai.us/tags.json"

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": "anime-role-dataset-builder/1.0"
            }
        )

    def resolve(self, keyword: str):

        keyword = keyword.lower().strip()

        try:

            resp = self.session.get(
                self.API_URL,
                params={
                    "search[name_matches]": f"{keyword}*",
                    "limit": 20
                },
                timeout=20
            )

            resp.raise_for_status()

            tags = resp.json()

            if not tags:
                return None

            tags.sort(
                key=lambda x: x.get("post_count", 0),
                reverse=True
            )

            best = tags[0]

            logger.info(
                f"{keyword} -> {best['name']} "
                f"(posts={best['post_count']})"
            )

            return best["name"]

        except Exception as e:
            logger.error(e)
            return None