from django.db import models




# Create your models here.

class QAData(models.Model):
    question_title = models.TextField(verbose_name='问题标题')
    question_content = models.TextField(verbose_name='问题内容', blank=True)
    author_name = models.CharField(verbose_name='答主昵称', max_length=100, blank=True)
    answer_time = models.DateTimeField(verbose_name='回答时间', null=True, blank=True)
    agree_count = models.IntegerField(verbose_name='赞同数', default=0)
    comment_count = models.IntegerField(verbose_name='评论数', default=0)
    answer_content = models.TextField(verbose_name='回答内容')
    word_segmentation = models.TextField(verbose_name='分词结果', blank=True)
    keywords = models.TextField(verbose_name='关键词列表', blank=True)

    def __str__(self):
        return self.question_title[:50]