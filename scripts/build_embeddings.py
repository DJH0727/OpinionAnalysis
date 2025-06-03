# scripts/build_embeddings.py

import os
import sys
import django
import pickle
from tqdm import tqdm
import re

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OpinionAnalysis.settings")
django.setup()

from scripts.bert_encoder import BERTEncoder
from frontend.models import QAData

encoder = BERTEncoder("../utils/models/bge-base-zh")

embedding_list = []

os.makedirs("embeddings", exist_ok=True)
print("Encoding QAData to embeddings...")

for record in tqdm(QAData.objects.all()):
    text = f"{record.question_title or ''}。{record.question_content or ''}。{record.answer_content or ''}"
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        continue

    try:
        emb = encoder.encode(text)
        embedding_list.append({
            "id": record.id,
            "embedding": emb,
        })
    except Exception as e:
        print(f"Error processing record {record.id}: {e}")

# 保存为本地文件
with open("embeddings/embeddings.pkl", "wb") as f:
    pickle.dump(embedding_list, f)

print(f"Finished! Saved {len(embedding_list)} embeddings to embeddings/embeddings.pkl")
