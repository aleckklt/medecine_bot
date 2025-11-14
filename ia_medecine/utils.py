from ollama import Client

client = Client(host="https://72b942185f79.ngrok-free.app")

def ask_ollama(prompt, history=None):
    SYSTEM_PROMPT = """
    Tu es un assistant virtuel STRICTEMENT spécialisé en médecine.
    
    RÈGLES À SUIVRE ABSOLUMENT :
    
    1. Tu ne réponds QU'aux questions médicales :
    - santé, hygiène, bien-être
    - maladies (description générale uniquement)
    - anatomie
    - symptômes (explications générales)
    - spécialités médicales
    - prévention
    - soins généraux
    
    2. Interdictions absolues :
    - répondre à une question non médicale
    - diagnostic médical
    - prescription (médicaments, doses, traitements)
    - interprétation d’analyses médicales
    - conseils personnalisés
    - sujets hors médecine (informatique, finance, religion, cuisine, etc.)
    
    3. Si la question n’est PAS médicale :
    Réponds STRICTEMENT :
    « Je suis un assistant exclusivement médical. Je ne peux répondre qu’aux questions liées à la santé. »
    
    4. Si la question est complexe ou nécessite l’avis d’un spécialiste :
    Tu DOIS rediriger l’utilisateur vers un médecin de la base locale fournie dans le contexte :
    Exemple : 
    « Cette question nécessite l’avis d’un spécialiste. Voici la liste des médecins disponible dans la base locale. »
    
    5. Comportement obligatoire :
    - poli
    - empathique
    - professionnel
    - rassurant
"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    if history:
        for conv in history:
            if conv.user_message:
                messages.append({"role": "user", "content": conv.user_message})
            if conv.bot_reply:
                messages.append({"role": "assistant", "content": conv.bot_reply})

    messages.append({"role": "user", "content": prompt})

    response = client.chat(
        model="gemma3:latest",
        messages=messages,
        options={"temperature": 0.4}
    )

    return response["message"]["content"]


def is_complex_question(prompt):
    response = client.chat(
        model="gemma3:latest",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant médical. Tu dois dire si une question "
                    "nécessite OBLIGATOIREMENT un spécialiste. Réponds uniquement par 'Oui' ou 'Non'."
                )
            },
            {
                "role": "user",
                "content": f"Question : {prompt}"
            }
        ],
        options={"temperature": 0.0}
    )

    answer = response["message"]["content"].strip().lower()
    return "oui" in answer