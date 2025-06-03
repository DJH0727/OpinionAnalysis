from utils.common import get_file_type
from utils.logger import Logger
from doc_project.nlp_utils import nlp_utils_funcs

"""
词性标注、实体识别、生成摘要、文本挖掘、情感分析（可选）、
"""
logger = Logger("doc_project.doc_analysis")
analysis_types = ['pos', 'ner', 'summarize', 'text_mining', 'sentiment']
analysis_strs = ['词性标注', '实体识别', '生成摘要', '文本挖掘', '情感分析']
analysis_output_files = ["pos_analysis.html", "ner_analysis.html", "summarize_analysis.html", "text_mining_analysis.html", "sentiment_analysis.html"]

def doc_analysis_get_result(analysis_str, file_name):
    try:
        index = analysis_strs.index(analysis_str)
        analysis_type = analysis_types[index]
        logger.info(f'执行分析类型：{analysis_str}，文件名：{file_name}')
        if not is_type_filename_match(analysis_type, file_name):
            return '文件类型不匹配，请检查输入关键词和文件类型是否匹配。'

        preview_html = nlp_utils_funcs[analysis_type](file_name)
        return {
            'output_file': analysis_output_files[index],
            'preview': preview_html,
        }

    except ValueError as e:
        logger.error(f'分析类型错误：{analysis_str}，错误信息：{e}')
        return '暂不支持该功能，请检查输入关键词和文件类型是否匹配。'

def is_type_filename_match(analysis_type, file_name):
    file_type = get_file_type(file_name)
    if file_type == 'doc':
        if analysis_type == 'pos' or analysis_type == 'ner' or analysis_type == 'summarize'  or analysis_type == 'sentiment':
            return True
    elif file_type == 'zip':
        if analysis_type == 'text_mining':
            return True
    else:
        return False

