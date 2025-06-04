import os
import pickle
import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity

from OpinionAnalysis.settings import STATIC_URL, BASE_DIR
from frontend.models import QAData
from qa_project.deepseek import inference_answer_without_image, inference_answer_with_image, get_vqa_questions
from qa_project.image_recognition import get_vqa_answer, captioning_image, extract_text_from_image
from qa_project.question_understanding import ques_understanding
import utils.common as common
from utils.loaded_model import bge_tokenizer, bge_model
from utils.logger import Logger

logger = Logger(name='qa_project.QASystem')


def qa_get_reply(question,file_name=None):
    common.current_reply_status = "understanding question"
    logger.info(f"Understanding question")
    question_result = ques_understanding(question)
    keywords = question_result['keywords']

    common.current_reply_status = "searching answer"
    logger.info(f"Searching answer")
    ans =search_answer(question=question,keywords=keywords)
    if ans is None:
        return "抱歉，没有找到答案。"


    #TODO: 图像描述（如果有）
    caption = ""
    vqa_answers = []
    text = []
    if file_name:
        common.current_reply_status = "recognizing picture"
        file_path = os.path.join(STATIC_URL, "uploads", file_name)
        caption = captioning_image(file_path)
        #TODO: 获取vqa 问题
        vqa_questions = get_vqa_questions(caption, question)
        #TODO: vqa answer
        vqa_answers = get_vqa_answer(image_path=file_path, questions=vqa_questions)
        #TODO: 识别文本
        text = extract_text_from_image(file_path)





    # TODO: 推理答案
    common.current_reply_status = "inferencing answer"
    logger.info(f"Inferencing answer")


    if file_name:
         inference_result = inference_answer_with_image(question=question,
                                                        answers=ans,
                                                        caption=caption,
                                                        vqa_answers=vqa_answers,
                                                        text=text)
    else:
        inference_result = inference_answer_without_image(question, ans)
    common.current_reply_status = "finished"

    result = inference_result['content']
    return result




embedding_path = os.path.join(BASE_DIR, "utils/models/embeddings/embeddings.pkl")
with open(embedding_path, "rb") as f:
    embedding_list = pickle.load(f)

weight_map = {
    "similarity": 0.6,
    "agree_count": 0.2,
    "comment_count": 0.1,
    "keywords_count": 0.1,
}
def search_answer(question,keywords,top_k=5):
    """
      综合语义相似度、点赞数、评论数和关键词命中数，对问答数据进行搜索排序。
    """
    if not keywords:
        return None
    # 编码用户问题
    query_vec = encode(question).reshape(1, -1)  # (1, 768)
    # 构建数据库向量矩阵
    db_vecs = np.array([item["embedding"] for item in embedding_list])

    # 计算余弦相似度
    sims = cosine_similarity(query_vec, db_vecs)[0]  # (N,)

    #获取candidate_multiplier*top_k个结果
    candidate_multiplier=5
    candidate_idx = sims.argsort()[-candidate_multiplier*top_k:][::-1]
    candidate_ids = [embedding_list[i]["id"] for i in candidate_idx]

    records = QAData.objects.filter(id__in=candidate_ids)
    id_to_record = {rec.id: rec for rec in records}

    #获取评论数和点赞数
    agree_counts = []
    comment_counts = []
    keyword_hits = []
    for idx in candidate_idx:
        rid = embedding_list[idx]["id"]
        rec = id_to_record.get(rid)
        agree_counts.append(rec.agree_count if rec else 0)
        comment_counts.append(rec.comment_count if rec else 0)
        # 关键词命中数（标题+内容+回答里出现了几个关键词）
        text = f"{rec.question_title or ''} {rec.question_content or ''} {rec.answer_content or ''}".lower()
        hit_count = sum(kw.lower() in text for kw in keywords)
        keyword_hits.append(hit_count)

    #归一化权重
    norm_agree = normalize_scores(agree_counts)
    norm_comment = normalize_scores(comment_counts)
    norm_sim = normalize_scores(sims[candidate_idx])
    norm_kw = normalize_scores(keyword_hits)

    # 计算最终排序分数
    total_scores = (
            weight_map["similarity"] * norm_sim +
            weight_map["agree_count"] * norm_agree +
            weight_map["comment_count"] * norm_comment +
            weight_map["keywords_count"] * norm_kw
    )

    # 8. 综合排序
    final_idx = np.argsort(-total_scores)[:top_k]
    answers = []
    for i in final_idx:
        idx = candidate_idx[i]
        item = embedding_list[idx]
        rec = id_to_record.get(item["id"])
        if rec:
            answers.append(rec.answer_content)
    logger.info(f"Search answers: {answers}")
    return answers


def encode(text: str) -> np.ndarray:
    inputs = bge_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = bge_model(**inputs)
    cls_vec = outputs.last_hidden_state[:, 0, :]  # [CLS] 向量
    return cls_vec.squeeze().numpy()

# 归一化分数
def normalize_scores(arr):
    arr = np.array(arr, dtype=float)
    max_val = arr.max()
    if max_val == 0:
        return arr
    return arr / max_val

