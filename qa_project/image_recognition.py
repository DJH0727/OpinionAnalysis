import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from PIL import Image
from OpinionAnalysis.settings import BASE_DIR
import os
from utils.logger import Logger

logger = Logger("qa_project.image_recognition")

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


def get_vqa_answer(image_path, questions):
    results = []
    # 加载图片并预处理
    raw_image = Image.open(image_path).convert('RGB')
    for question in questions:
        # 每个问题单独处理
        inputs = vqa_processor(raw_image, question, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            out = vqa_model.generate(**inputs, max_new_tokens=20, num_beams=5)
        answer = vqa_processor.decode(out[0], skip_special_tokens=True)
        logger.info(f"VQA | Q: {question} → A: {answer}")
        results.append({
            "question": question,
            "answer": answer
        })

    return results