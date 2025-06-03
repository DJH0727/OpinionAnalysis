from openai import OpenAI
from utils.logger import Logger

logger = Logger("qa_project.deepseek")

client = OpenAI(api_key="sk-e2320a6385f64cffba2c9c0b2ffbe91b", base_url="https://api.deepseek.com")
#推理
def inference_answer_without_image(question,answers):
    #TODO: 推理答案，根据检索的答案调用deepseek api 进行答案推理
    logger.info(f"Inference question: {question}")
    context = "\n\n".join(f"文本{i + 1}: {ans}" for i, ans in enumerate(answers))
    response = client.chat.completions.create(
        model="deepseek-reasoner",#deepseek-chat
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的舆情分析师，擅长从多个文本片段中综合分析并得出准确结论。"
            },
            {
                "role": "user",
                "content":
                    "请你扮演舆情分析师，根据以下问题和多个相关的文本片段，推理出一个准确的结论。\n\n"
                    f"问题：{question}\n\n"
                    f"相关文本片段：\n{context}\n\n"
                    "请注意：\n"
                    "1. 请只根据提供的问题和文本片段进行推理，不得引入其他背景知识；\n"
                    "2. 问题和文本片段直接可能不存在关联，请判断其关联性；\n"
                    "3. 文本片段之间可能存在重复或矛盾，请合理判断其可信度和关联性；\n"
                    "4. 除了你的答案，不要提供任何其他信息，包括引言或说明性句子；\n"
                    "5. 输出格式必须为 markdown，对应字段如下：\n"
                    "- answer：最终结论，总结为一段话；\n"
                    "- reason：推理过程，用markdown语法解释如何得出结论；\n\n"
                    "示例输出：\n"
                    "## 推理过程: \n{reason}\n## 结论: \n{answer}"
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


def get_vqa_questions(caption, user_question=None, max_questions=5):
    prompt = (
        f"You are a helpful assistant aiding image understanding through Visual Question Answering (VQA).\n\n"
        f"Your task is to generate up to {max_questions} concise, informative, and diverse English questions "
        f"that help complete and enrich the following image description.\n\n"
        f"Image caption (incomplete): {caption}\n"
    )

    if user_question:
        prompt += f"\nAdditionally, the user asked: {user_question}\n"

    prompt += (
        "\nThink like an investigator trying to uncover more details about the image.\n"
        "Your questions should help clarify unclear aspects, explore fine-grained details, or verify assumptions in the caption.\n\n"
        "Output a numbered list of up to 5 questions. Do not explain anything. Only list questions."
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You generate VQA-style questions to improve image understanding."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    lines = response.choices[0].message.content.strip().split("\n")
    questions = [
        line.split(".", 1)[-1].strip()
        for line in lines
        if "." in line and len(line.split(".", 1)[-1].strip()) > 0
    ]

    return questions[:max_questions]


def inference_answer_with_image(question, answers, caption,vqa_answers,text):
    logger.info(f"Inference (with image) question: {question}")
    context = "\n\n".join(f"文本{i + 1}: {ans}" for i, ans in enumerate(answers))
    vqa_context = "\n".join(f"Q{i + 1}: {qa['question']}\nA{i + 1}: {qa['answer']}" for i, qa in enumerate(vqa_answers))
    prompt = (
        "你是一位专业的舆情分析师，擅长结合文本与图像信息进行综合推理和分析。\n\n"
        f"问题：{question}\n\n"
        f"图像文本识别结果：{text}\n\n"
        f"图像内容描述：{caption}\n\n"
        f"图像相关问答信息：\n{vqa_context}\n\n"
        f"相关文本片段：\n{context}\n\n"
        "请注意：\n"
        "1. 请综合 问题、图像文本识别结果、图像描述、图像问答信息、文本片段 进行推理，仅在这些信息的基础上作答；\n"
        "2. 图像和文本可能互相补充或存在矛盾，请合理判断其可信度；\n"
        "3. 图像描述要根据图像内容描述和相关问答信息进行准确描述，图像内容描述和问答信息可能存在歧义，不必过分解读；\n"
        "4. 除了你的答案，不要提供任何其他信息，包括引言或说明性句子；\n"
        "5. 输出格式必须为 markdown，对应字段如下：\n"
        "- caption：图像描述，结合图像文本识别结果、图像内容描述和相关问答信息进行准确描述，中文；\n"
        "- answer：最终结论，总结为一段话；\n"
        "- reason：推理过程，用markdown语法解释如何得出结论；\n\n"
        "示例输出：\n"
        "## 图像描述：\n{caption}\n## 推理过程: \n{reason}\n## 结论: \n{answer}"
    )

    response = client.chat.completions.create(
        model="deepseek-reasoner",  # 或 deepseek-reasoner
        messages=[
            {"role": "system", "content": "你是一个专业的舆情分析师，擅长多模态舆情理解与推理。"},
            {"role": "user", "content": prompt}
        ],
        stream=False,
    )

    logger.info(f"content: {response.choices[0].message.content}")

    return {
        "reasoning_content": response.choices[0].message.content,  # 保留原始JSON字符串
        "content": response.choices[0].message.content
    }
