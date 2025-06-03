import os

import hanlp
import re

from OpinionAnalysis.settings import BASE_DIR
from utils.loaded_model import tokenize_hanlp, tokenizer_bert, model_bert
from utils.logger import Logger
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
logger = Logger(name='question_understanding')




def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

stopwordsUrl = os.path.join(BASE_DIR, 'qa_project/resources/data/stopwords.txt')
stopwords = load_stopwords(stopwordsUrl)

def remove_stopwords(words):
    return [w for w in words if w not in stopwords]
def clean_text(text: str) -> str:
    # 1. 去除多余空白（包括换行、制表符）
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    # 2. 去除特殊符号（保留中文、英文、数字、常用标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？,.!? ]', '', text)
    return text

def segment_text(text: str):
    return tokenize_hanlp(text)

def extract_keywords_hanlp_bert(filtered_words, text, top_k=5):
    # 用 BERT 得到每个词的向量（取词对应的第一个token的embedding）
    embeddings = []
    for word in filtered_words:
        inputs = tokenizer_bert(word, return_tensors='pt')
        with torch.no_grad():
            outputs = model_bert(**inputs)
        # 取第一个token的embedding作为该词向量
        emb = outputs.last_hidden_state[0][0].numpy()
        embeddings.append(emb)

    if len(embeddings) == 0:
        return []

    # 计算句子向量（用 CLS 向量）
    inputs_full = tokenizer_bert(text, return_tensors='pt')
    with torch.no_grad():
        outputs_full = model_bert(**inputs_full)
    cls_embedding = outputs_full.last_hidden_state[0][0].numpy()

    # 计算每个词向量与句子向量的余弦相似度
    sims = cosine_similarity([cls_embedding], embeddings)[0]
    top_indices = sims.argsort()[-top_k:][::-1]

    keywords = [filtered_words[i] for i in top_indices]
    return keywords



def ques_understanding(text: str):
    # 文本清洗
    cleaned_text = clean_text(text)

    result = segment_text(cleaned_text)
    #分词
    tokens = result['tok/fine']
    logger.info("分词结果: %s", tokens)
    #去除停用词
    filtered_tokens = remove_stopwords(tokens)
    logger.info("去除停用词后: %s", filtered_tokens)
    # 关键词抽取
    keywords = extract_keywords_hanlp_bert(filtered_tokens, cleaned_text)
    logger.info("关键词抽取结果: %s", keywords)
    # 词性标注
    pos_tags = result['pos/ctb']
    logger.info("词性标注结果: %s", pos_tags)
    # 命名实体识别
    named_entities = result['ner/msra']
    logger.info("命名实体识别结果: %s", named_entities)

    return{
        "tokens": tokens,
        "filtered_tokens": filtered_tokens,
        "keywords": keywords,
        "pos_tags": pos_tags,
        "named_entities": named_entities
    }



