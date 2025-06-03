
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