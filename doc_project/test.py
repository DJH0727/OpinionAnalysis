import os
import zipfile

mining_file_names=['cluster_0_wordcloud.png',
                   'cluster_1_wordcloud.png',
                   'cluster_2_wordcloud.png',
                   'cluster_3_wordcloud.png',
                   'cluster_4_wordcloud.png',
                   'cluster_5_wordcloud.png',
                   'tsne_scatter.png',]
def zip_visualization_results(output_dir, zip_file_path):
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

# 🧪 示例调用：
zip_visualization_results('output/wordcloud_and_tsne', 'output/visualization.zip')