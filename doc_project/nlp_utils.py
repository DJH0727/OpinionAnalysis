from doc_project.common_utils import get_doc_text, save_html_file
from doc_project.generater import generate_pos_html_str, generate_pos_html_page, generate_ner_html_str, \
    generate_ner_html_page
from utils.loaded_model import tokenize_hanlp
from utils.logger import Logger

logger = Logger("doc_project.nlp_utils")

def pos_analysis(file_name):
    #TODO: 词性标注实现
    # 1. 读取文件文本
    text = get_doc_text(file_name)
    # 2. 使用HanLP模型进行分析
    result = tokenize_hanlp(text)
    # 3. result是dict，词语和词性列表
    tokens = result['tok/fine']  # 细粒度分词
    pos_tags = result['pos/ctb']  # 词性标注（一般用pku标准）
    logger.info("pos_result: " + ", ".join([f"{tok}/{tag}" for tok, tag in zip(tokens, pos_tags)]))
    # 4. 组装成HTML字符串，词和词性颜色标注
    #预览
    preview_str = generate_pos_html_str(tokens, pos_tags)
    #生成HTML页面
    html = generate_pos_html_page(tokens, pos_tags)
    save_html_file("pos_analysis.html", html)
    return preview_str


def ner_analysis(file_name):
    text = get_doc_text(file_name)
    result = tokenize_hanlp(text)
    tokens = result.get('tok/fine', [])
    ner_tags = result.get('ner/msra', [])

    tags = ['O'] * len(tokens)

    for ent_text, ent_type, start_idx, end_idx in ner_tags:
        # BIO格式标注，首字B-类型，后续I-类型
        tags[start_idx] = 'B-' + ent_type
        for i in range(start_idx + 1, end_idx):
            tags[i] = 'I-' + ent_type

    logger.info("ner_result: " + ", ".join([f"{tok}/{tag}" for tok, tag in zip(tokens, tags)]))

    html = generate_ner_html_page(tokens, tags)
    save_html_file("ner_analysis.html", html)
    logger.info("实体识别结果页面已保存：ner_analysis.html")

    preview_str = generate_ner_html_str(tokens, tags)
    return preview_str


def summarize_analysis(file_name):
    # 文档摘要实现
    pass

def text_mining_analysis(file_name):
    # 文本挖掘实现
    pass

def sentiment_analysis(file_name):
    # 情感分析实现
    pass

nlp_utils_funcs = {
    'pos': pos_analysis,
    'ner': ner_analysis,
    'summarize': summarize_analysis,
    'text_mining': text_mining_analysis,
    'sentiment': sentiment_analysis,
}

