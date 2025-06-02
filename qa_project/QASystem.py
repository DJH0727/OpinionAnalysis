import json
import os
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering

from OpinionAnalysis.settings import BASE_DIR, STATIC_URL
from qa_project.question_understanding import ques_understanding
import utils.common as common
from utils.logger import Logger
from PIL import Image

logger = Logger(name='qa_project.QASystem')

from openai import OpenAI

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
    if file_name:
        common.current_reply_status = "recognizing picture"
        file_path = os.path.join(STATIC_URL, "uploads", file_name)
        caption = captioning_image(file_path)

    # TODO: 推理答案
    common.current_reply_status = "inferencing answer"
    logger.info(f"Inferencing answer")


    if file_name:
         inference_result = inference_answer_with_image(question, ans, caption)
    else:
        inference_result = inference_answer_without_image(question, ans)
    common.current_reply_status = "finished"

    result = json.loads(inference_result['content'])
    answer = result['answer']
    reason = result['reason']
    return {
        "answer": answer,
        "reason": reason,
        "caption": caption
    }

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




client = OpenAI(api_key="sk-e2320a6385f64cffba2c9c0b2ffbe91b", base_url="https://api.deepseek.com")
#推理
def inference_answer_without_image(question,answers):
    #TODO: 推理答案，根据检索的答案调用deepseek api 进行答案推理
    logger.info(f"Inference question: {question}")
    context = "\n\n".join(f"文本{i + 1}: {ans}" for i, ans in enumerate(answers))
    response = client.chat.completions.create(
        model="deepseek-reasoner",#deepseek-chat
        messages=[
            {"role": "system",
             "content":"你是一个专业的舆情分析师。\n"
             },
            {
                "role": "user",
                "content":
                "请根据下面的问题和相关的多个答案片段，综合分析并给出最准确的回答。\n"
                f"问题: {question}\n\n"
                f"相关答案片段:\n{context}\n\n"
                "请只根据提供的答案片段进行推理，不得添加与片段无关的内容。\n"
                "请按json格式输出，{\"answer\": \"...\", \"reason\": \"...\"}\n"
                "其中answer字段为结论，reason字段为推理过程。字段中为markdown格式。\n"
            },
        ],
        stream=False,
    )
    logger.info(f"content: {response.choices[0].message.content}")
    #logger.info(f"reasoning_content: {response.choices[0].message.reasoning_content}")

    return {
        "reasoning_content": response.choices[0].message.reasoning_content,
        "content": response.choices[0].message.content
    }

def inference_answer_with_image(question,answers,caption):
    #TODO: 推理答案，根据检索的答案调用deepseek api 进行答案推理
    return {
        "reasoning_content": '',
        "content": '{\"answer\": \"...\", \"reason\": \"...\"}'
    }


# 加载模型
#cap_model_path = "./resources/models/blip-image-captioning"
cap_model_path = os.path.join(BASE_DIR, "qa_project/resources/models/blip-image-captioning")
cap_processor = BlipProcessor.from_pretrained(cap_model_path, local_files_only=True)
cap_model = BlipForConditionalGeneration.from_pretrained(cap_model_path, local_files_only=True)
cap_model.eval()
cap_model.to("cpu")
logger.info("loading captioning model success")
def captioning_image(image_path):
    #TODO: 图像描述
    image = Image.open(image_path).convert("RGB")
    inputs = cap_processor(images=image,return_tensors="pt")
    # 生成时设置更多参数，提高描述质量和完整性
    # out = cap_model.generate(
    #     **inputs,
    #     max_new_tokens=50,  # 控制最大长度
    #     num_beams=5,  # 束搜索，质量稳定
    #     do_sample=False,  # 关闭采样，确定性输出
    #     early_stopping=True,  # 达到结束条件提前停止
    #     repetition_penalty=1.1,  # 避免重复
    #     no_repeat_ngram_size=2,  # 防止重复n-gram
    # )

    #打开采样，不再是固定的贪心/束搜索，生成更丰富多变的句子。
    out = cap_model.generate(
        **inputs,
        max_new_tokens=100,  # 控制最多生成 50 个 token
        num_beams=3,  # 束搜索，提升质量
        repetition_penalty=1.1,  # 惩罚重复
        do_sample=True,  # 启用采样
        top_p=0.9,  # nucleus sampling
        temperature=0.9  # 随机性控制
    )
    caption = cap_processor.decode(out[0], skip_special_tokens=True)
    logger.info(f"Caption: {caption}")
    return caption



#vqa_model_path = "./resources/models/blip-vqa-base"
vqa_model_path = os.path.join(BASE_DIR, "qa_project/resources/models/blip-vqa-base")
vqa_processor = BlipProcessor.from_pretrained(vqa_model_path, local_files_only=True)
vqa_model = BlipForQuestionAnswering.from_pretrained(vqa_model_path, local_files_only=True)
vqa_model.eval()
vqa_model.to("cpu")
logger.info("loading vqa model success")
def vqa_answer(image_path, question):
    # 加载图片
    raw_image = Image.open(image_path).convert('RGB')
    # 描述图片
    # 预处理图像和问题
    inputs = vqa_processor(raw_image, question, return_tensors="pt", padding=True, truncation=True)
    # 推理
    with torch.no_grad():
        out = vqa_model.generate(**inputs, max_new_tokens=20, num_beams=5)
    # 解码输出
    answer = vqa_processor.decode(out[0], skip_special_tokens=True)
    logger.info(f"vqa Answer: {answer}")
    return answer


if __name__ == '__main__':
    image_name = "image.jpg"
    image_path1 = "D:/Program/Python/scientificProject/OpinionAnalysis/static/uploads/" + image_name
    #captioning_image(image_path1)
    question1 = "最近大家对某品牌手机有什么看法？"
    # answers = [
    # "我觉得电池特别不给力，充不上一天，老是得带充电宝。",
    # "拍照真心一般，尤其晚上拍的照片都模糊，看起来很失望。",
    # "更新系统之后感觉手机反应变慢了，玩游戏都卡顿，挺烦的。",
    # "用了一段时间，系统还是挺稳定的，就是偶尔会有点发热。",
    # "客服服务态度不错，但物流有点慢，收到手机花了好几天。"
    # ]
    # inference_answer(question1,answers)
    #search_answer(question1)
    #vqa_answer(image_path1, question1)