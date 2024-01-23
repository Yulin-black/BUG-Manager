import base
from web import models


# 使用离线脚本添加一条 价格策略
def run():
    exists = models.PricePolicy.objects.filter(category=1, title="个人免费版").exists()
    if not exists:
        models.PricePolicy.objects.create(
            category=1,
            title="个人免费版",
            price=1,
            project_num=3,
            project_number=2,
            project_space=20,
            per_file_size=5
        )

if __name__ == '__main__':
    run()