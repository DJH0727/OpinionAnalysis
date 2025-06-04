
color_map = {
    'NN': '#ffadad',  # 名词
    'VV': '#ffd6a5',  # 动词
    'JJ': '#fdffb6',  # 形容词
    'AD': '#caffbf',  # 副词
    'PN': '#9bf6ff',  # 代词
}

def generate_pos_html_page(tokens, pos_tags, title="词性标注结果"):
    assert len(tokens) == len(pos_tags), "tokens 与 pos_tags 长度不一致"

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <title>{title}</title>
  <style>
    body {{
      font-family: "Microsoft YaHei", sans-serif;
      padding: 20px;
      line-height: 1.8;
    }}
    span.word {{
      padding: 3px 6px;
      margin: 2px;
      border-radius: 4px;
      display: inline-block;
      color: #000;
      font-weight: 600;
      cursor: default;
      user-select: none;
    }}
  </style>
</head>
<body>
  <h2>{title}</h2>
  {generate_pos_legend_html_str()}
  <div>
"""

    for token, tag in zip(tokens, pos_tags):
        if tag in color_map:
            color = color_map[tag]
            html += f'<span class="word" style="background-color:{color};" title="{tag}">{token}</span> '
        else:
            # 没有对应颜色，直接普通显示
            html += token + " "

    html += """
  </div>
</body>
</html>"""

    return html

    # color_map = {
    #     'NN': '#ffadad', 'VV': '#ffd6a5', 'JJ': '#fdffb6', 'AD': '#caffbf',
    #     'PN': '#9bf6ff', 'PU': '#bdb2ff', 'CD': '#ffc6ff', 'DT': '#fffffc',
    #     'r': '#bde0fe', 'v': '#a0c4ff', 'n': '#d0f4de', 'd': '#ffeaa7', 'w': '#fab1a0'
    # }
def generate_pos_html_str(tokens, pos_tags, max_tokens=200):
    html_parts = []
    for token, tag in zip(tokens[:max_tokens], pos_tags[:max_tokens]):  # 限制词数
        if tag in color_map:
            color = color_map[tag]
            html_parts.append(
                f'<span style="background-color:{color};padding:2px;border-radius:4px;" title="{tag}">{token}</span>'
            )
        else:
            html_parts.append(token)

    if len(tokens) > max_tokens:
        html_parts.append('...')  # 超出部分用省略号表示

    return ''.join(generate_pos_legend_html_str()) + '<div>' + ' '.join(html_parts) + '</div>'

def generate_pos_legend_html_str():
    # 图例说明部分
    legend_parts = ['<div style="margin-bottom:10px;"><strong>词性标注图例：</strong>']
    tag_name_map = {
        'NN': '名词',
        'VV': '动词',
        'JJ': '形容词',
        'AD': '副词',
        'PN': '代词',
    }
    for tag, color in color_map.items():
        name = tag_name_map.get(tag, tag)
        legend_parts.append(
            f'<span style="background-color:{color};padding:2px 6px;margin-right:5px;'
            f'border-radius:4px;display:inline-block;" title="{tag}">{name}</span>'
        )
    legend_parts.append('</div>')
    return ''.join(legend_parts)










# 颜色映射，可根据实体类型扩展
ner_color_map = {
    'PERSON': '#ffadad',       # 人名
    'LOCATION': '#ffd6a5',     # 地点
    'ORGANIZATION': '#9bf6ff', # 机构名
    'DATE': '#caffbf',         # 时间
    'O': '#ffffff'             # 非实体
}

def generate_ner_html_str(tokens, tags, max_tokens=200):
    html_parts = []

    # 限制显示数量
    tokens = tokens[:max_tokens]
    tags = tags[:max_tokens]

    i = 0
    while i < len(tokens):
        tag = tags[i]
        if tag.startswith("B-"):
            ent_type = tag[2:]
            color = ner_color_map.get(ent_type, '#e0e0e0')
            entity_tokens = [tokens[i]]
            i += 1
            while i < len(tokens) and tags[i] == f"I-{ent_type}":
                entity_tokens.append(tokens[i])
                i += 1
            entity_text = "".join(entity_tokens)
            html_parts.append(
                f'<span style="background-color:{color};padding:2px 4px;border-radius:4px;margin:1px;" '
                f'title="{ent_type}">{entity_text}</span>'
            )
        else:
            html_parts.append(tokens[i])
            i += 1

    return generate_ner_legend_html_str() + '<div>' + ' '.join(html_parts) + '</div>'


def generate_ner_legend_html_str():
    # 图例说明部分
    legend_parts = ['<div style="margin-bottom:10px;"><strong>实体类型图例：</strong>']
    tag_name_map = {
        'PERSON': '人名',
        'LOCATION': '地点',
        'ORGANIZATION': '机构',
        'DATE': '时间'
    }
    for ent_type, color in ner_color_map.items():
        if ent_type == 'O':
            continue
        name = tag_name_map.get(ent_type, ent_type)
        legend_parts.append(
            f'<span style="background-color:{color};padding:2px 6px;margin-right:5px;'
            f'border-radius:4px;display:inline-block;" title="{ent_type}">{name}</span>'
        )
    legend_parts.append('</div>')
    return ''.join(legend_parts)

def generate_ner_html_page(tokens, tags, title="命名实体识别结果"):
    """
    根据 tokens 和 BIO 格式 tags 生成高亮实体的 HTML 页面。
    :param tokens: 分词列表
    :param tags: BIO 标签列表，如 ['O', 'B-PERSON', 'I-PERSON', 'O']
    :param title: 页面标题
    :return: HTML 字符串
    """
    assert len(tokens) == len(tags), "tokens 和 tags 长度不一致"

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    body {{
      font-family: "Microsoft YaHei", sans-serif;
      padding: 20px;
      line-height: 1.8;
      color: #000;
    }}
    .entity {{
      padding: 3px 6px;
      margin: 2px;
      border-radius: 4px;
      display: inline-block;
      color: #000;
    }}
  </style>
</head>
<body>
  <h2>{title}</h2>
  {generate_ner_legend_html_str()}
  <div>
"""

    i = 0
    while i < len(tokens):
        tag = tags[i]
        if tag.startswith("B-"):
            ent_type = tag[2:]
            color = ner_color_map.get(ent_type, "#e0e0e0")
            entity_tokens = [tokens[i]]
            i += 1
            while i < len(tokens) and tags[i] == f"I-{ent_type}":
                entity_tokens.append(tokens[i])
                i += 1
            entity_text = "".join(entity_tokens)
            html += f'<span class="entity" style="background-color:{color};" title="{ent_type}">{entity_text}</span> '
        else:
            html += f'{tokens[i]} '
            i += 1

    html += """
  </div>
</body>
</html>
"""
    return html


def generate_text_mining_html_str(output_dir="/static/downloads/", num_clusters=5):
    html = f"""
    <div class="text-mining-result">
        <div class="image-block">
            <h3>t-SNE 聚类可视化</h3>
            <img src="{output_dir}/tsne_scatter.png" alt="t-SNE 聚类图" style="max-width: 100%; border: 1px solid #ccc;" />
        </div>
    """

    for i in range(num_clusters):
        html += f"""
        <div class="image-block">
            <h4>Cluster {i} 词云图</h4>
            <img src="{output_dir}/cluster_{i}_wordcloud.png" alt="Cluster {i} 词云图" style="max-width: 100%; border: 1px solid #ccc;" />
        </div>
        """

    html += "</div>"
    return html





def structured_data_to_html(structured_data, is_preview=False):
    html_parts = [
        '<html>',
        '<head>',
        '<meta charset="utf-8">',
        '<title>文档展示</title>',
        '<style>',
        '''
        #docx-viewer {
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background-color: #f9f9f9;
        }
        #docx-viewer p {
            margin-bottom: 1em;
        }
        #docx-viewer table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background-color: white;
        }
        #docx-viewer table, #docx-viewer th, #docx-viewer td {
            border: 1px solid #aaa;
        }
        #docx-viewer td {
            padding: 8px;
            vertical-align: top;
        }
        #docx-viewer img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 16px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        ''',
        '</style>',
        '</head>',
        '<body>',
        '<div id="docx-viewer">'
    ]

    for item in structured_data:
        if item['type'] == 'paragraph':
            font_size = item.get('font_size', 12)
            if font_size is None:
                font_size = 12
            text = item.get('text', '')
            font_size_px = int(font_size * 1.33)
            html_parts.append(f'<p style="font-size:{font_size_px}px;">{text}</p>')

        elif item['type'] == 'table':
            html_parts.append('<table>')
            for row in item['data']:
                html_parts.append('<tr>')
                for cell in row:
                    html_parts.append(f'<td>{cell}</td>')
                html_parts.append('</tr>')
            html_parts.append('</table>')

        elif item['type'] == 'image':
            path = item.get('path', '')
            if is_preview:
                path = f'/static/downloads/{path}'
            html_parts.append(f'<img src="{path}" alt="图片">')

    html_parts.append('</div></body></html>')

    return '\n'.join(html_parts)
