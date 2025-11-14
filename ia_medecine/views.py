from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import ask_ollama, is_complex_question
from .models import Conversation, CategorieMedecine, Medecin

def chat_page(request):
    categories = CategorieMedecine.objects.all()
    return render(request, "ia_medecine/chatbot.html", {"categories": categories})

@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        if not user_message:
            return JsonResponse({"reply": "Veuillez entrer un message valide."})

        history = Conversation.objects.order_by("created_at")
        bot_reply = ask_ollama(user_message, history)
        Conversation.objects.create(user_message=user_message, bot_reply=bot_reply)

        complex_flag = is_complex_question(user_message)
        return JsonResponse({"reply": bot_reply, "complex": complex_flag})

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def medecins_par_categorie(request, categorie_id):
    try:
        categorie = CategorieMedecine.objects.get(id=categorie_id)
        medecins = Medecin.objects.filter(specialite__icontains=categorie.nom)
        data = [
            {
                "nom": m.nom,
                "specialite": m.specialite,
                "email": m.email or "Non renseigné",
                "telephone": m.telephone or "Non renseigné"
            }
            for m in medecins
        ]
        return JsonResponse({"categorie": categorie.nom, "medecins": data})
    except CategorieMedecine.DoesNotExist:
        return JsonResponse({"error": "Catégorie non trouvée."}, status=404)