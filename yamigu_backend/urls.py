from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authorization.urls import api_urlpattern as auth_url
from core.urls import api_urlpattern as meeting_url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import rest_framework.permissions as permissions
schema_view = get_schema_view(
openapi.Info(
	title="yamigu API",
	default_version='v1',
	description="yamigu API documentation",
	terms_of_service="https://www.google.com/policies/terms/",
	contact=openapi.Contact(email="khc146@gmail.com"),
	license=openapi.License(name="BSD License"),
),
validators=['flex', 'ssv'],
public=True,
permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(meeting_url)),
    url(r'^api/', include(auth_url)),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




