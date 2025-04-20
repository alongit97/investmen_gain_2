from django.urls import include, path
from otree.urls import urlpatterns as otree_urlpatterns
from investment_experiment_demo import views

custom_urlpatterns = [
    path('download_excel/', views.DownloadExcel.as_view(), name='download_excel'),
]

urlpatterns = custom_urlpatterns + otree_urlpatterns
