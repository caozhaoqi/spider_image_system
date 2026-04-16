#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 正则匹配工具

提供正则表达式匹配功能
"""

from re import Pattern

from ..jm_exception import ExceptionTool


class PatternTool:
    """正则匹配工具"""

    @classmethod
    def match_or_default(cls, html: str, pattern: Pattern, default):
        match = pattern.search(html)
        return default if match is None else match[1]

    @classmethod
    def require_match(cls, html: str, pattern: Pattern, msg, rindex=1):
        match = pattern.search(html)
        if match is not None:
            return match[rindex] if rindex is not None else match

        ExceptionTool.raises_regex(
            msg,
            html=html,
            pattern=pattern,
        )

    @classmethod
    def require_not_match(cls, html: str, pattern: Pattern, *, msg_func):
        match = pattern.search(html)
        if match is None:
            return

        ExceptionTool.raises_regex(
            msg_func(match),
            html=html,
            pattern=pattern,
        )
