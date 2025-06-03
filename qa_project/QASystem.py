import json
import os


from OpinionAnalysis.settings import  STATIC_URL
from qa_project.deepseek import inference_answer_without_image, inference_answer_with_image, get_vqa_questions
from qa_project.image_recognition import get_vqa_answer, captioning_image
from qa_project.question_understanding import ques_understanding
import utils.common as common
from utils.logger import Logger

logger = Logger(name='qa_project.QASystem')


def qa_get_reply(question,file_name=None):
    common.current_reply_status = "understanding question"
    logger.info(f"Understanding question")
    question_result = ques_understanding(question)
    keywords = question_result['keywords']

    common.current_reply_status = "searching answer"
    logger.info(f"Searching answer")
    ans =search_answer(keywords)
    if ans is None:
        return "抱歉，没有找到答案。"

    #TODO: 图像描述（如果有）
    caption = ""
    vqa_answers = []
    if file_name:
        common.current_reply_status = "recognizing picture"
        file_path = os.path.join(STATIC_URL, "uploads", file_name)
        caption = captioning_image(file_path)
        #TODO: 获取vqa 问题
        vqa_questions = get_vqa_questions(caption, question)
        #TODO: vqa answer
        vqa_answers = get_vqa_answer(image_path=file_path, questions=vqa_questions)


    # TODO: 推理答案
    common.current_reply_status = "inferencing answer"
    logger.info(f"Inferencing answer")


    if file_name:
         inference_result = inference_answer_with_image(question=question,
                                                        answers=ans,
                                                        caption=caption,
                                                        vqa_answers=vqa_answers)
    else:
        inference_result = inference_answer_without_image(question, ans)
    common.current_reply_status = "finished"

    result = inference_result['content']
    return result




def search_answer(keywords):
    #TODO: 根据问题搜索答案

    #TODO: 根据关键词检索答案
    answers = [
    "我觉得电池特别不给力，充不上一天，老是得带充电宝。",
    "拍照真心一般，尤其晚上拍的照片都模糊，看起来很失望。",
    "更新系统之后感觉手机反应变慢了，玩游戏都卡顿，挺烦的。",
    "用了一段时间，系统还是挺稳定的，就是偶尔会有点发热。",
    "客服服务态度不错，但物流有点慢，收到手机花了好几天。"
    ]
    return answers


