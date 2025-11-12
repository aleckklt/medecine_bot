from ollama import Client
from .models import CategorieMedecine, Medecin

client = Client(host='http://localhost:11434')
#client = Client(host='https://516fc142efc4.ngrok-free.app')

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

    return "\n\n".join(context_parts)


def ask_ollama(prompt, history=None):

    local_context = get_context(prompt)

    system_prompt = (
        """Tu es un assistant médical virtuel bienveillant, professionnel et empathique sachant répondre aux questions de base en médecine de tout genre."
        Règles strictes :"
        1. Tu ne réponds qu’aux questions médicales de bases."
        2. Tu ne fournis jamais de définition ou d’information pour des sujets n'ayant aucun lien avec la médecine."
        3. Tu ne poses jamais de diagnostic ni ne prescris de traitement."
        4. Si une question médicale est trop complexe ou spécialisée, tu proposes calmement un médecin spécialiste disponible dans la base locale avec son contact."
        Comportement attendu :"
        - Sois toujours poli, empathique et chaleureux."
        - Ne fournis jamais d’information hors domaine médical."
        - Propose un médecin uniquement si la question est complexe."""
        )
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
        model="gemma3:latest",
        messages=messages,
        options={"temperature": 0.4}
    )

    return response["message"]["content"]