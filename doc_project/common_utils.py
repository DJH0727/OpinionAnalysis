import os

import chardet

from OpinionAnalysis.settings import STATIC_URL

output_dir = os.path.join(STATIC_URL, 'downloads')

def get_doc_text(file_name):
    file_path = os.path.join(STATIC_URL, 'uploads', file_name)
    # 先以二进制模式读取部分内容检测编码
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)  # 读取前10000字节检测编码
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    if encoding is None:
        encoding = 'utf-8'  # 默认编码，防止 None
    # 再用检测到的编码读取文本
    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        text = f.read()

    return text

def save_html_file(filename, html_str):
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(html_str)