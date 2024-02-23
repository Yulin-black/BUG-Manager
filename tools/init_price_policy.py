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
    models.PricePolicy.objects.create(
        category=2,
        title="VIP",
        price=100,
        project_num=50,
        project_number=10,
        project_space=10,
        per_file_size=500
    )

    models.PricePolicy.objects.create(
        category=2,
        title="SVIP",
        price=200,
        project_num=150,
        project_number=100,
        project_space=100,
        per_file_size=1024
    )

    models.PricePolicy.objects.create(
        category=2,
        title="SSVIP",
        price=200,
        project_num=250,
        project_number=300,
        project_space=300,
        per_file_size=2048
    )

if __name__ == '__main__':
    run()