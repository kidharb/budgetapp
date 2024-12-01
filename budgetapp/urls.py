from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PDFContentViewSet

router = DefaultRouter()
router.register(r'pdfcontents', PDFContentViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('view_pdfs/', views.view_pdfs, name='view_pdfs'),
    path('delete_pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    path('plot_balance_graph/', views.plot_balance_graph, name='plot_balance_graph'),
    path('login/', views.google_login, name='login'),
    path('callback/', views.callback, name='callback'),
    path('api/', include(router.urls)),
]

