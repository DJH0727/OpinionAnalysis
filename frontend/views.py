import os
import uuid

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from qa_project.QASystem import qa_get_reply
from utils import common
from utils.logger import Logger
from OpinionAnalysis import settings

logger = Logger(name='frontend.views')
# Create your views here.
def home(request):
    return render(request, 'chat.html')


@require_GET
def getReply(request):
    response = {
        "status": 200,
        "replyType": "text",
        "reply": "Hello, world!"
    }
    text = request.GET.get("text", "")
    op_type = request.GET.get("opType", "")
    file_name = request.GET.get("fileName", "")
    logger.info("getReply: 文本: %s 类型: %s 文件名: %s",
                text, op_type, file_name if file_name else "null")


    result = {}
    if file_name:
       file_type = common.get_file_type(file_name)
       if file_type == "img":
           result = qa_get_reply(question=text, file_name=file_name)
       elif file_type == "unknown":
           result = "暂不支持该类型文件"
    else:
        result = qa_get_reply(question=text)


    replyStr = str(result)

    response['status'] = 200
    response['replyType'] = 'text'#text, image, file
    response['reply'] = replyStr
    return JsonResponse(response)


@csrf_exempt
def uploadFile(request):
    if request.method == 'POST' and request.FILES.get('file'):
        upload_file = request.FILES['file']
        original_name = upload_file.name
        file_ext = os.path.splitext(original_name)[1]  # 获取扩展名
        unique_name = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        # 定义保存路径，直接保存在项目的根目录下
        save_path = os.path.join(settings.BASE_DIR, 'static/uploads/', unique_name)

        # 如果目录不存在，则创建
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        try:
            # 写入文件到磁盘
            with open(save_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)

            # 返回上传结果
            logger.info("uploadFile: 文件名: %s 保存路径: %s", original_name, "uploads/"+unique_name)
            return JsonResponse({'status': 200, 'message': '文件上传成功', 'filename': unique_name})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '无效的请求'}, status=400)


def getReplyStatus(request):
    response = {
        "status": 200,
        "replyStatus": common.reply_status_mapping[common.current_reply_status]
    }
    return JsonResponse(response)