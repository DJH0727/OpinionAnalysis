import os

from hanlp_restful import HanLPClient

from OpinionAnalysis.settings import BASE_DIR
from doc_project.common_utils import get_doc_text, save_html_file, save_txt_file, unzip_file, read_all_csv_files, \
    read_and_combine_csv_files, preprocess_texts, perform_clustering_and_visualization, zip_visualization_results
from doc_project.generater import generate_pos_html_str, generate_pos_html_page, generate_ner_html_str, \
    generate_ner_html_page, generate_text_mining_html_str
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

HanLP = HanLPClient('https://www.hanlp.com/api', auth=None, language='zh')
def summarize_analysis(file_name ):
    # 摘要生成实现
    text = get_doc_text(file_name)
    summary = HanLP.abstractive_summarization(text)
    logger.info("摘要: " + summary)
    save_txt_file("summarize_analysis.txt", summary)
    return summary

def text_mining_analysis(file_name):
    # 文本挖掘实现
    #1. 解压文件
    temp_dir = os.path.join(BASE_DIR, 'static', 'uploads', 'temp')
    file_path = os.path.join(BASE_DIR,'static', 'uploads', file_name)
    unzip_file(file_path, temp_dir)
    #2. 读取文件,获取所有csv文件路径
    file_paths = read_all_csv_files(temp_dir)
    #3. 读取csv文件内容，进行分析
    combined_df = read_and_combine_csv_files([file_path for file_path, _ in file_paths])
    #4. 文本预处理
    raw_texts = combined_df['text'].dropna().astype(str).tolist()
    texts_cleaned = preprocess_texts(raw_texts)
    #5. 文本挖掘分析
    perform_clustering_and_visualization(texts_cleaned, num_clusters=5)

    #6. 生成HTML
    preview_str = generate_text_mining_html_str()

    #7. 打包压缩文件
    zip_visualization_results('text_mining_analysis.zip')
    return preview_str



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


