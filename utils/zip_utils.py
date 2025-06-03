import json
import zipfile
from pathlib import Path
from typing import List


def list_zip_files(zip_path: str) -> List[str]:
    """列出 ZIP 文件中的所有文件名"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        return zip_ref.namelist()


def read_file_from_zip(zip_path: str, file_name: str) -> str:
    """读取 ZIP 中指定文件的内容（作为字符串返回）"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zip_ref.open(file_name) as f:
            return f.read().decode('utf-8')  # 或使用其他编码


def extract_zip(zip_path: str, output_dir: str = './unzipped') -> None:
    """将 ZIP 文件全部解压到指定目录"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

if __name__ == '__main__':
    zip_path = 'example.zip'
    # 列出所有文件
    file_list = list_zip_files(zip_path)
    print(file_list)
    # 读取某个文件内容
    content = read_file_from_zip(zip_path, 'example/test1.json')
    json_data = json.loads(content)
    print(json_data)

