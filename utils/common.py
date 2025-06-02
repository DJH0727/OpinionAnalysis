reply_type_mapping = {
    "text": "text",
    "image": "image",
    "file": "file",}
reply_status_mapping = {
    "idle":"空闲中",
    "understanding question": "理解问题中",
    "searching answer": "搜索答案中",
    "recognizing picture": "识别图片中",
    "inferencing answer": "推理答案中",
    "finished": "finished",}
current_reply_status = "idle"


def get_file_type(file_name):
    extension = file_name.lower().split('.')[-1]

    img_extensions = {"png", "jpg", "jpeg", "bmp", "gif", "webp", "tiff", "svg"}
    doc_extensions = {"doc", "docx", "txt", "md", "rtf", "pdf", "ppt", "pptx", "xls", "xlsx", "csv"}

    if extension in img_extensions:
        return "img"
    elif extension in doc_extensions:
        return "doc"
    else:
        return "unknown"