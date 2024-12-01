from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('budgetapp.urls')),  # Add your app's URL configurations
    path('', TemplateView.as_view(template_name='static/index.html')),  # Add this line
]

