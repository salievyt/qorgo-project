import io
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Text, Link, Asset, FAQ, Pricing, Document

class LandingContentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @extend_schema(responses={200: {'type': 'object', 'description': 'Тексты, ссылки, FAQ, тарифы и документы лендинга'}})
    def get(self, request):
        links = {x.key: request.build_absolute_uri(x.asset.url) if x.asset_id else x.url for x in Link.objects.select_related('asset')}
        pricing = Pricing.objects.first()
        return Response({'texts': dict(Text.objects.values_list('key', 'value')), 'links': links,
            'presentation_url': links.get('presentation', '/QORGO_Presentation.pptx'),
            'faqs': list(FAQ.objects.filter(active=True).values_list('question', 'answer')),
            'pricing': pricing.data if pricing else {},
            'documents': list(Document.objects.filter(active=True).values('slug', 'title', 'body'))}, headers={'Cache-Control': 'no-store'})

class AssetView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    @extend_schema(responses={200: {'type': 'string', 'format': 'binary'}})
    def get(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)
        response = FileResponse(io.BytesIO(bytes(asset.data)), as_attachment=True, filename=asset.filename, content_type='application/octet-stream')
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'no-store'
        return response
