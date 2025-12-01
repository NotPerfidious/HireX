from django.urls import path
from .views import Jobs,AddSkill

urlpatterns = [
    path("", Jobs.as_view()),              # /jobs/  → GET (list), POST
    path("<int:id>/", Jobs.as_view()),     # /jobs/5/ → GET (single), PUT, DELETE
    path("skill/",AddSkill.as_view())
]
