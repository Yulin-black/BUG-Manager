from rest_framework import serializers
from web import models


class CatalogSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Wiki
        fields = ["id","title","parent"]