from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from simditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey


# 通用评论
class Comment(MPTTModel):
    title = models.CharField('标题', max_length=128, blank=True, null=True)
    content = RichTextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # mptt树形结构
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    '''
    记录二级评论回复给谁
    限制评论最多只能两级:
    一级评论人为 a，二级评论人为 b（parent 为 a），三级评论人为 c（parent 为 b）。
    因为我们不允许评论超过两级，因此将 c 的 parent 重置为 a，reply_to 记录为 b，这样就能正确追溯真正的被评论者了
    '''
    reply_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='repliers'
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return self.title
