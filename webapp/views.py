from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from django.apps import apps
from django.db import models, connection, migrations

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from rest_framework.parsers import JSONParser

from .models import Total_files
from .serializers import  GeneralSerializer

import json
import glob


def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model

def one_time_setup():
    directory = settings.FILE_UPLOAD

    for filename in glob.glob(directory + "/*.json"):
        f = open(filename)
        data = json.load(f)
        fields = {}
        for key in data[0].keys():
            if key == "id":
                continue
            datatype = type(data[0][key])
            if datatype is int:
                fields[key] = models.IntegerField()
            else: 
                fields[key] = models.CharField(max_length=255)

        model_name =  os.path.basename(os.path.splitext(filename)[0])
        created_model = create_model(model_name, fields, 'webapp')

# Create your views here.
class CreateListModelMixin(object):

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CreateListModelMixin, self).get_serializer(*args, **kwargs)


class GeneralViewSet(CreateListModelMixin, ModelViewSet):

    @property
    def model(self):
        return apps.get_model(app_label=str(self.kwargs['app_label']), model_name=str(self.kwargs['model_name']))

    def get_queryset(self):
        model = self.model
        return model.objects.all()     

    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer


class GeneralViewSet2(ModelViewSet):
    @property
    def model(self):
        return apps.get_model(app_label=str(self.kwargs['app_label']), model_name=str(self.kwargs['model_name']))

    def get_queryset(self):
        pk = self.kwargs['pk']
        model = self.model
        return model.objects.filter(pk=pk)


    def get_serializer_class(self):
        GeneralSerializer.Meta.model = self.model
        return GeneralSerializer

# from .tasks import model_upload_task
@api_view(['POST'])
@parser_classes((MultiPartParser,))
def model_upload(request, format=None):

    uploaded_file = request.FILES['file']

    data = JSONParser().parse(uploaded_file.open())
    # model_upload_task.delay(data, uploaded_file.name)

    fields = {}
    for key in data[0].keys():
        if key == "id":
            continue

        datatype = type(data[0][key])
        if datatype is int:
            fields[key] = models.IntegerField()
        else: 
            fields[key] = models.CharField(max_length=255)

    model_name =  os.path.splitext(uploaded_file.name)[0]
    created_model = create_model(model_name, fields, 'webapp')

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(created_model)

    for record in data:
        created_obj = created_model(**record)
        created_obj.save()

    # save file
    fs = FileSystemStorage()
    filename = fs.save( os.path.join(settings.FILE_UPLOAD, uploaded_file.name), uploaded_file)
    
    return Response({'Message': 'Successful'})