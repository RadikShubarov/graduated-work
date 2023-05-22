from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('<slug:host>', views.HostDetailView.as_view(), name='host-detail')
    # path('<slug:hosts>', views.show_host_stat('slug'), name='host-details')
]
