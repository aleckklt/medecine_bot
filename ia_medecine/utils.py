from ollama import Client
from .models import CategorieMedecine, Medecin

#client = Client(host='http://localhost:11434')
client = Client(host="https://76f99ec34722.ngrok-free.app")
def get_context(prompt):
    query_lower = prompt.lower()
    context_parts = []

    for cat in CategorieMedecine.objects.all():
        if cat.nom.lower() in query_lower:
            context_parts.append(f"Domaine médical : {cat.nom}\n{cat.description}")
            break

    for med in Medecin.objects.all():
        if med.specialite.lower() in query_lower or med.nom.lower() in query_lower:
            context_parts.append(
                f"Spécialiste : {med.nom}\n"
                f"Spécialité : {med.specialite}\n"
                f"Contact : {med.email or 'Email non disponible'} | {med.telephone or 'Téléphone non disponible'}"
            )
            break

    if not context_parts:
        return "Aucune donnée médicale spécifique trouvée dans la base."

    return context_parts

def ask_ollama(prompt, history=None):
    local_context = get_context(prompt)
    system_prompt = """Tu es un assistant médical virtuel, conçu pour répondre uniquement aux questions liées à la médecine. "
        Voici les règles strictes que tu dois suivre :"
        1. Réponses uniquement médicales : Tu ne réponds qu'aux questions qui sont directement liées à la santé, "
        la médecine, les maladies, les traitements, les spécialités médicales et tout ce qui concerne le bien-être humain."
           - Exemple de question acceptable : 'Qu'est-ce que la cardiologie ?', 'Quels sont les symptômes du diabète ?'"
           - Exemple de question non acceptable : 'C'est quoi Python ?', 'Comment cuisiner un gâteau ?'"
        2. Pas de réponse à des questions générales : Si une question ne concerne pas directement un domaine médical, "
        tu ne dois pas y répondre et dire poliment que tu ne peux répondre qu'aux questions médicales."
           - Exemple de refus : 'Désolé, je ne peux répondre qu'à des questions médicales. Pour des questions générales, "
        je te conseille de consulter une ressource appropriée.'"
        3. Pas de diagnostic ni de prescription : Tu ne fais jamais de diagnostic médical ni de prescription. "
        Tu peux fournir des informations générales, mais tu ne dois pas remplacer un médecin."
        4. Si la question est complexe : Si une question médicale est complexe ou nécessite l'expertise d'un spécialiste, "
        tu rediriges calmement l'utilisateur vers un médecin disponible dans la base locale avec son contact."
           - Exemple de recommandation : 'Cette question semble nécessiter un spécialiste."
        5. Comportement attendu : Tu dois toujours être poli, empathique et chaleureux, tout en restant professionnel. "
        Si tu ne peux pas répondre à une question ou si elle est trop complexe, tu dois toujours recommander de consulter un professionnel de santé.\n"
        6. Contexte local : Toujours vérifier les catégories médicales locales et les médecins disponibles dans la base de données "
        avant de répondre aux questions complexes ou spécialisées."
        Tu n'es pas censé répondre à des questions qui ne touchent pas directement à la médecine ou la santé."""
        
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for conv in history:
            if conv.user_message:
                messages.append({"role": "user", "content": conv.user_message})
            if conv.bot_reply:
                messages.append({"role": "assistant", "content": conv.bot_reply})

    messages.append({
        "role": "user",
        "content": f"Contexte local :\n{local_context}\n\nQuestion : {prompt}"
    })

    response = client.chat(
        model="llama3.2:latest",
        messages=messages,
        options={"temperature": 0.4}
    )

    return response["message"]["content"]

def is_complex_question(prompt):
    response = client.chat(
        model="gemma3:latest",
        messages=[
            {"role": "system", "content": "Tu es un assistant médical qui ne traite que les question médicale de base. Tu ne réponds à aucune question hors sujet médicale."},
            {"role": "user", "content": f"Cette question nécessite-t-elle un médecin spécialiste ? Réponds uniquement par Oui ou Non.\nQuestion : {prompt}"}
        ],
        options={"temperature": 0.0}
    )
    answer = response["message"]["content"].strip().lower()
    return "oui" in answer