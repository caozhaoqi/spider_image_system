from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def test():
    proxy = {
        "proxyType": "manual",
        "httpProxy": "http://192.168.199.26:8080",  # 代理服务器地址和端口
        "ftpProxy": "http://192.168.199.26:8080",
        "sslProxy": "http://192.168.199.26:8080",
        "noProxy": "",
        "proxyAutoconfigUrl": ""
    }

    ## 创建浏览器驱动程序并设置代理参数
    options = webdriver.ChromeOptions()
    options.set_capability("proxy", proxy)
    driver = webdriver.Chrome(options=options)
    key_word = "keqing"
    # 打开目标网页
    driver.get("https://www.pixiv.net/tags/" + key_word + "/illustrations")

    # 等待页面加载完毕
    time.sleep(20)

    # 定位并点击图片元素，假设点击后会跳转到新的页面或链接
    # 这里只是一个示例，实际点击的元素可能会有所不同
    image_element = driver.find_element(By.CSS_SELECTOR, "img")  # 根据实际情况修改选择器
    image_element.click()

    # 等待页面加载完毕
    time.sleep(2)

    # 获取当前页面的URL（如果需要的话）
    current_url = driver.current_url
    print("当前URL:", current_url)

    # 关闭浏览器驱动程序
    driver.quit()


if __name__ == '__main__':
    test()
