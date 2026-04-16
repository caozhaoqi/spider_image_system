#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JM Comic 发送邮件插件

功能：发送邮件通知
"""

from .base import JmOptionPlugin


class SendEmailPlugin(JmOptionPlugin):
    """发送邮件插件"""
    plugin_key = 'send_email'

    def invoke(self, to_addr, subject='JM Comic Download Complete', content='', **kwargs) -> None:
        """
        发送邮件通知
        
        :param to_addr: 收件人地址
        :param subject: 邮件主题
        :param content: 邮件内容
        :param kwargs: SMTP服务器配置
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
        except ImportError:
            self.warning_lib_not_install('smtplib')
            return

        smtp_server = kwargs.get('smtp_server', 'smtp.gmail.com')
        smtp_port = kwargs.get('smtp_port', 587)
        from_addr = kwargs.get('from_addr')
        password = kwargs.get('password')

        self.require_param(from_addr, '发件人地址不能为空')
        self.require_param(password, '发件人密码不能为空')
        self.require_param(to_addr, '收件人地址不能为空')

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_addr, password)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            self.log(f'邮件发送成功: {to_addr}')
        except Exception as e:
            self.log(f'邮件发送失败: {e}', 'error')
