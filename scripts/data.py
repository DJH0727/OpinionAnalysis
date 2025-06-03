import os
import re
from datetime import datetime

import django
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
# 设置 Django 环境变量（替换为你的 settings 模块路径）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OpinionAnalysis.settings')  # 假设项目名是 OpinionAnalysis

# 初始化 Django
django.setup()
from django.utils import timezone
from frontend.models import QAData

def safe_int(value):
    if not value:
        return 0
    # 去除空白字符和不可见字符
    clean_value = str(value).strip().replace('\u200b', '').replace('\n', '').replace(' ', '')
    try:
        return int(clean_value)
    except ValueError:
        return 0


def parse_datetime(value):
    if not value:
        return None
    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', value)
    if match:
        time_str = match.group(1)
        try:
            dt_naive = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            # 转成带时区的datetime
            dt_aware = timezone.make_aware(dt_naive)
            return dt_aware
        except ValueError:
            return None
    else:
        return None
def import_csv_to_db(csv_path):
    df = pd.read_csv(csv_path)
    df.fillna('', inplace=True)

    for _, row in tqdm(df.iterrows(), total=len(df), desc="导入进度"):
        QAData.objects.create(
            question_title=row.get('问题标题', ''),
            question_content=row.get('问题内容', ''),
            author_name=row.get('答主昵称', ''),
            answer_time=parse_datetime(row.get('回答时间', '')),
            agree_count=safe_int(row.get('赞同数', 0)),
            comment_count=safe_int(row.get('评论数', 0)),  # 这里修正了评论数字段
            answer_content=row.get('回答内容', ''),
            word_segmentation=row.get('分词结果', ''),
            keywords=row.get('关键词列表', '')
        )

#删除重复数据
def delete_duplicate_data():


    # key: (title, content, answer), value: list of IDs
    content_map = defaultdict(list)

    for qa in QAData.objects.all():
        key = (
            (qa.question_title or '').strip(),
            (qa.question_content or '').strip(),
            (qa.answer_content or '').strip()
        )
        content_map[key].append(qa.id)

    # 保留每组重复数据的第一条，删除其余
    to_delete = []
    for ids in content_map.values():
        if len(ids) > 1:
            to_delete.extend(ids[1:])  # 保留第一条，删除后面的

    QAData.objects.filter(id__in=to_delete).delete()
    print(f"✅ 删除了 {len(to_delete)} 条重复记录")

if __name__ == '__main__':
    delete_duplicate_data()