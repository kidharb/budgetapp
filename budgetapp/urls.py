from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('view_pdfs/', views.view_pdfs, name='view_pdfs'),
]
