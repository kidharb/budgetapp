from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Home URL
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('view_pdfs/', views.view_pdfs, name='view_pdfs'),
     path('delete_pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
]
