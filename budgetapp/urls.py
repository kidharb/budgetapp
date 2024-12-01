from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CSVContentViewSet

router = DefaultRouter()
router.register(r'csvcontents', CSVContentViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('view_transactions/', views.view_transactions, name='view_transactions'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('plot_balance_graph/', views.plot_balance_graph, name='plot_balance_graph'),
    path('login/', views.google_login, name='login'),
    path('callback/', views.callback, name='callback'),
    path('api/', include(router.urls)),
]

