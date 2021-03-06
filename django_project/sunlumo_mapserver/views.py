# -*- coding: utf-8 -*-
import logging
import subprocess
import os.path

from django.http import HttpResponse, Http404
from django.views.generic import View
from django.conf import settings

from braces.views import JSONResponseMixin

from sunlumo_project.models import Project

from .renderer import Renderer
from .featureinfo import FeatureInfo
from .project import SunlumoProject
from .utils import writeParamsToJson, str2bool, hex2rgb

LOG = logging.getLogger(__name__)


class UpperParamsMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.req_params = {
            key.upper(): request.GET[key] for key in request.GET.keys()
        }
        return super(UpperParamsMixin, self).dispatch(
            request, *args, **kwargs
        )


class ProjectDetails(UpperParamsMixin, JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):

        project = Project.objects.get(pk=settings.SUNLUMO_PROJECT_ID)
        sl_project = SunlumoProject(project.project_path)

        return self.render_json_response(sl_project.getDetails())


class GetMapView(UpperParamsMixin, JSONResponseMixin, View):
    def _parse_request_params(self, request):
        if not(all(param in self.req_params for param in [
                'BBOX', 'WIDTH', 'HEIGHT', 'SRS', 'FORMAT', 'LAYERS',
                'TRANSPARENCIES', 'REQUEST'])):
            raise Http404

        try:
            request = self.req_params.get('REQUEST')
            bbox = [float(a) for a in self.req_params.get('BBOX').split(',')]
            image_size = [
                int(a) for a in (
                    self.req_params.get('WIDTH'),
                    self.req_params.get('HEIGHT'))
            ]
            srs = int(self.req_params.get('SRS').split(':')[-1])
            image_format = self.req_params.get('FORMAT').split('/')[-1]
            transparent = str2bool(self.req_params.get('TRANSPARENT', False))
            bgcolor = hex2rgb(self.req_params.get('BGCOLOR', '0xFFFFFF'))
            layers = [
                layer.strip()
                for layer in self.req_params.get('LAYERS').split(',')
            ]
            if self.req_params.get('QUERY_LAYERS'):
                query_layers = [
                    layer.strip()
                    for layer in self.req_params.get('QUERY_LAYERS').split(',')
                ]
            else:
                query_layers = []
            if self.req_params.get('X') and self.req_params.get('Y'):
                click_point = [
                    int(self.req_params.get('X')),
                    int(self.req_params.get('Y'))
                ]
            else:
                click_point = []
            transparencies = [
                int(a)
                for a in self.req_params.get('TRANSPARENCIES').split(',')
                if len(a) > 0
            ]
        except:
            # return 404 if any of parameters are missing or not parsable
            raise Http404

        # map must have a value
        if not(request):
            raise Http404

        # check if image format is supported
        if image_format not in ['png', 'jpeg', 'png8']:
            raise Http404

        params = {
            'bbox': bbox,
            'image_size': image_size,
            'srs': srs,
            'image_format': image_format,
            'transparent': transparent,
            'bgcolor': bgcolor,
            'layers': layers,
            'transparencies': transparencies,
            'request': request,
            'query_layers': query_layers,
            'click_point': click_point
        }

        return params

    def get(self, request, *args, **kwargs):
        params = self._parse_request_params(request)

        project = Project.objects.get(pk=settings.SUNLUMO_PROJECT_ID)

        if params.get('request') == 'GetMap':
            sl_project = Renderer(project.project_path)
            img = sl_project.render(params)

            return HttpResponse(img, content_type=params.get('image_format'))
        else:
            sl_project = FeatureInfo(project.project_path)
            features = sl_project.identify(params)

            return self.render_json_response(features)


class GetLegendGraphicView(UpperParamsMixin, JSONResponseMixin, View):
    def _parse_request_params(self, request):
        if not(all(param in self.req_params for param in [
                'FORMAT', 'LAYER', 'REQUEST'])):
            raise Http404

        try:
            request = self.req_params.get('REQUEST')
            image_size = [
                int(a) for a in (
                    self.req_params.get('WIDTH', -1),
                    self.req_params.get('HEIGHT', -1))
            ]
            image_format = self.req_params.get('FORMAT').split('/')[-1]
            layer = self.req_params.get('LAYER').strip()
        except:
            # return 404 if any of parameters are missing or not parsable
            raise Http404

        # map must have a value
        if not(request):
            raise Http404

        # check if image format is supported
        if image_format not in ['png', 'jpeg', 'png8']:
            raise Http404

        params = {
            'image_format': image_format,
            'image_size': image_size,
            'layer': layer,
            'request': request
        }

        return params

    def get(self, request, *args, **kwargs):
        params = self._parse_request_params(request)

        project = Project.objects.get(pk=settings.SUNLUMO_PROJECT_ID)

        sl_project = Renderer(project.project_path)
        img = sl_project.getLegendGraphic(params)
        return HttpResponse(img, content_type=params.get('image_format'))


class PrintPDFView(UpperParamsMixin, View):
    def _parse_request_params(self, request):
        if not(all(param in self.req_params for param in [
                'BBOX', 'LAYOUT', 'LAYERS', 'TRANSPARENCIES'])):
            raise Http404

        try:
            bbox = [float(a) for a in self.req_params.get('BBOX').split(',')]
            srs = int(self.req_params.get('SRS').split(':')[-1])
            layers = [
                layer.strip()
                for layer in self.req_params.get('LAYERS').split(',')
            ]
            layout = self.req_params.get('LAYOUT')
            transparencies = [
                int(a)
                for a in self.req_params.get('TRANSPARENCIES').split(',')
                if len(a) > 0
            ]
        except:
            # return 404 if any of parameters are missing or not parsable
            raise Http404

        if not(layout):
            # composer template should not be empty
            raise Http404

        return {
            'bbox': bbox,
            'layout': layout,
            'layers': layers,
            'transparencies': transparencies,
            'srs': srs
        }

    def get(self, request, *args, **kwargs):

        params = self._parse_request_params(request)

        params.update({'sl_project_id': settings.SUNLUMO_PROJECT_ID})

        tmpFile = writeParamsToJson(params)

        # printing requires a subprocess call
        proc = subprocess.call(['python', 'manage.py', 'print_map', tmpFile])
        if proc:
            # subprocess did not exit cleanly
            return HttpResponse(status=500)

        with open(tmpFile + '.pdf', 'r') as pdfFile:
            data = pdfFile.read()

        resp = HttpResponse(data, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
            os.path.basename(tmpFile)
        )
        return resp
