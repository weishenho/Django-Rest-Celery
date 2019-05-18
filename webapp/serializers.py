from rest_framework import serializers

class GeneralSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = '__all__' 