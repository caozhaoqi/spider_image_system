import fitz  # PyMuPDF


def read_pdf_main():
    # 打开PDF文件
    pdf_file = fitz.open("data/马克思主义基本原理（2023年版）.pdf")

    # 创建一个TXT文件并打开
    with open('data/output.txt', 'w', encoding='utf-8') as txt_file:
        # 遍历PDF的每一页
        for page_num in range(len(pdf_file)):
            # 获取当前页面的文本内容
            text = pdf_file[page_num].get_text()

            # 将文本写入TXT文件
            txt_file.write(text)


if __name__ == '__main__':
    read_pdf_main()
