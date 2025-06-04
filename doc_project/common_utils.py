import os
import random
import re
import json
import shutil
import zipfile
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from wordcloud import WordCloud
import numpy as np
from matplotlib.font_manager import FontProperties
import chardet
import jieba
import pandas as pd
from matplotlib import image as mpimg

from OpinionAnalysis.settings import STATIC_URL, BASE_DIR

output_dir = os.path.join(BASE_DIR,'static', 'downloads')

def get_doc_text(file_name):
    file_path = os.path.join(STATIC_URL, 'uploads', file_name)
    # 先以二进制模式读取部分内容检测编码
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)  # 读取前10000字节检测编码
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    if encoding is None:
        encoding = 'utf-8'  # 默认编码，防止 None
    # 再用检测到的编码读取文本
    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
        text = f.read()

    return text

def save_html_file(filename, html_str):
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(html_str)

def save_txt_file(filename, text):
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write(text)
def save_json_file(filename, data):
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

#解压文件
def unzip_file(zip_path, extract_dir='temp_extract'):
    # 如果目标文件夹存在，先删除
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)

    # 解压
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    return extract_dir
# 读取所有CSV文件，返回列表，元素为 (文件路径, DataFrame)
def read_all_csv_files(dir_path):
    """
    递归遍历指定目录，读取所有CSV文件，返回列表，元素为 (文件路径, DataFrame)
    """
    data_files = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = str(os.path.join(root, file))
                try:
                    df = pd.read_csv(file_path)
                    data_files.append((file_path, df))
                except Exception as e:
                    print(f"读取文件 {file_path} 出错: {e}")
    if not data_files:
        raise ValueError("目录内未找到任何CSV文件")
    return data_files

# 读取所有csv文件，返回列表，元素为 (文件路径, DataFrame)
def read_and_combine_csv_files(file_paths):
    dfs = []
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        dfs.append(df)
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

stopwords_path = os.path.join(BASE_DIR,'doc_project','resources','stopwords.txt')
stopwords = set()
with open(stopwords_path, encoding='utf-8') as f:
    for line in f:
        stopwords.add(line.strip())

# 文本清洗
def clean_text(text):
    # 去除非中文、非字母数字的字符（可以根据需求调整）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text)  # 多空格合并为一个空格
    text = text.strip()
    return text

# 分词并去除停用词
def tokenize_and_remove_stopwords(text):
    words = jieba.lcut(text)
    words_filtered = [w for w in words if w not in stopwords and len(w.strip()) > 0]
    return " ".join(words_filtered)


# 文本预处理
def preprocess_texts(texts):
    cleaned_texts = []
    for text in texts:
        text = clean_text(text)
        text = tokenize_and_remove_stopwords(text)
        cleaned_texts.append(text)
    return cleaned_texts





font_path = os.path.join(BASE_DIR,'doc_project', 'resources','simsun.ttc')
mask_image_path_list = [
    os.path.join(BASE_DIR,'doc_project','resources', 'wordcloud_template','girl.jpg'),
    os.path.join(BASE_DIR,'doc_project','resources', 'wordcloud_template','cat.jpg'),
    os.path.join(BASE_DIR,'doc_project','resources', 'wordcloud_template','xin.jpg'),
    os.path.join(BASE_DIR,'doc_project','resources', 'wordcloud_template','dog.png'),
]


def perform_clustering_and_visualization(texts_cleaned, num_clusters=5):
    # 向量化
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts_cleaned)

    # KMeans 聚类
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # t-SNE 降维
    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(X.toarray())

    # t-SNE 散点图
    plt.figure(figsize=(8, 6))
    for i in range(num_clusters):
        plt.scatter(X_tsne[labels == i, 0], X_tsne[labels == i, 1], label=f'Cluster {i}')
    plt.title('t-SNE 聚类可视化', fontproperties=FontProperties(fname=font_path) if font_path else None)
    plt.legend()
    tsne_path = os.path.join(output_dir, 'tsne_scatter.png')
    plt.savefig(tsne_path, bbox_inches='tight')
    plt.close()



    # 每类生成词云图
    for i in range(num_clusters):
        # 读取 mask 图像（如有）
        mask_image_path = mask_image_path_list[random.randint(0, len(mask_image_path_list) - 1)]
        mask_array = None
        if mask_image_path:
            mask_array = mpimg.imread(mask_image_path)
            if mask_array.ndim == 3 and mask_array.shape[2] == 4:
                mask_array = mask_array[:, :, :3]  # 去掉 alpha 通道
            if mask_array.dtype != np.uint8:
                mask_array = (mask_array * 255).astype(np.uint8)

        cluster_text = " ".join([texts_cleaned[j] for j in range(len(texts_cleaned)) if labels[j] == i])
        wordcloud = WordCloud(
            font_path=font_path,
            background_color='white',
            width=800, height=400,
            mask=mask_array,
        ).generate(cluster_text)
        wc_path = os.path.join(output_dir, f'cluster_{i}_wordcloud.png')
        wordcloud.to_file(wc_path)



mining_file_names=['cluster_0_wordcloud.png',
                   'cluster_1_wordcloud.png',
                   'cluster_2_wordcloud.png',
                   'cluster_3_wordcloud.png',
                   'cluster_4_wordcloud.png',
                   'cluster_5_wordcloud.png',
                   'tsne_scatter.png',]
def zip_visualization_results(zip_file_name):
    zip_file_path = os.path.join(output_dir, zip_file_name)
    """
    将指定目录下的词云图和聚类图打包成zip压缩包

    :param output_dir: 存放图像的文件夹路径
    :param zip_file_path: 最终压缩包输出路径
    """
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(output_dir):
            if file_name in mining_file_names:
                file_path = os.path.join(output_dir, file_name)
                arcname = os.path.basename(file_path)  # 压缩包中的文件名
                zipf.write(file_path, arcname)

