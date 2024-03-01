from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os


def log_encode(decode_key, cipher):
    """

    :param cipher:
    :param decode_key:
    :return:
    """

    # 创建一个加密器对象
    encryptor = cipher.encryptor()

    # 要加密的日志消息
    log_message = "2024-02-21 10:41:30.997 | INFO     | log.log_record:check_version:60 - system started, current SIS " \
                  "system version: v1.0.7-beta".encode()

    # 使用 PKCS7 填充对日志消息进行填充，使其长度适合加密
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(log_message) + padder.finalize()

    # 加密填充后的数据
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # 现在 ciphertext 包含加密后的日志消息
    print("加密后的日志:", ciphertext)
    return ciphertext


def log_decode(encode_key, cipher_text):
    """

    :param cipher_text:
    :param encode_key:
    :return:
    """
    # 解密过程
    # 创建一个相同的 Cipher 对象用于解密
    decrypt_cipher = Cipher(algorithms.AES(encode_key), modes.CBC(os.urandom(16)), backend=default_backend())

    # 创建一个解密器对象
    decryptor = decrypt_cipher.decryptor()

    # 解密数据
    decrypted_data = decryptor.update(cipher_text) + decryptor.finalize()

    # 移除 PKCS7 填充
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # 现在 unpadded_data 包含解密后的日志消息
    print("解密后的日志:", unpadded_data.decode())


if __name__ == '__main__':
    # 生成一个随机的 256 位 AES 密钥
    key = os.urandom(32)

    # 创建一个 AES Cipher 对象，使用 CBC 模式和一个随机的初始化向量 (IV)
    cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=default_backend())
    ciphertext = log_encode(key, cipher)
    log_decode(key, ciphertext)
