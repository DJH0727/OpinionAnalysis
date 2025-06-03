import os

from transformers import BertTokenizer, BertModel
import hanlp
from utils.logger import Logger
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from OpinionAnalysis.settings import BASE_DIR


logger = Logger("utils.loaded_model")




# 加载HanLP的分词模型和BERT预训练模型
tokenize_hanlp = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)

#加载Bert模型，用于分类
bert_model_path = os.path.join(BASE_DIR, 'utils/models/bert-base-cn')
tokenizer_bert = BertTokenizer.from_pretrained(bert_model_path,local_files_only=True)
model_bert = BertModel.from_pretrained(bert_model_path,local_files_only=True)
model_bert.eval()
logger.info("load bert model success")

# 加载BLIP图像描述模型
cap_model_path = os.path.join(BASE_DIR, "utils/models/blip-image-captioning")
cap_processor = BlipProcessor.from_pretrained(cap_model_path, local_files_only=True)
cap_model = BlipForConditionalGeneration.from_pretrained(cap_model_path, local_files_only=True)
cap_model.eval()
cap_model.to("cpu")
logger.info("load captioning model success")

# 加载BLIP视觉问答模型
vqa_model_path = os.path.join(BASE_DIR, "utils/models/blip-vqa-base")
vqa_processor = BlipProcessor.from_pretrained(vqa_model_path, local_files_only=True)
vqa_model = BlipForQuestionAnswering.from_pretrained(vqa_model_path, local_files_only=True)
vqa_model.eval()
vqa_model.to("cpu")
logger.info("load vqa model success")

