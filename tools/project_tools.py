

def init_issues_module(instance, modelObject):
    # 初始化 项目 问题类型 、 模块
    object_list = []
    for item in modelObject.PROJECT_INIT_LIST:
        object_list.append(modelObject(project=instance, title=item))
    # 批量添加
    modelObject.objects.bulk_create(object_list)