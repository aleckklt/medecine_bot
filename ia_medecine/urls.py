from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="chat_page"),
    path("api/chat/", views.chatbot_view, name="chatbot_view"),
    path("api/medecins/<int:categorie_id>/", views.medecins_par_categorie, name="medecins_par_categorie"),
]