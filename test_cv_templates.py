import os
from types import SimpleNamespace

os.makedirs("test_pdfs", exist_ok=True)

from cv_generator.services import generate_pdf


data = {
    "job_title": "Développeur Full Stack & DevOps",

    "experience": [
        {
            "title": "Développeur Full Stack",
            "subtitle": "Projet KIRA",
            "description": (
                "Développement d'une application Flutter "
                "avec backend Django REST Framework et "
                "intégration de services IA."
            ),
        },
        {
            "title": "Développeur Python",
            "subtitle": "Projet personnel",
            "description": (
                "Création d'API, gestion de bases de données "
                "et automatisation avec Python."
            ),
        },
    ],

    "education": [
        {
            "title": (
                "Licence en Mathématiques et Informatique "
                "Appliquées à la Gestion des Entreprises"
            ),
            "subtitle": (
                "Université Gamal Abdel Nasser de Conakry"
            ),
            "description": (
                "Formation en informatique, mathématiques, "
                "bases de données et systèmes."
            ),
        }
    ],

    "skills": [
        "Python",
        "Flutter",
        "Django",
        "Django REST Framework",
        "DevOps",
        "Docker",
        "Linux",
        "Git",
        "Intelligence Artificielle",
        "Cybersécurité",
    ],

    "projects": [
        {
            "title": "KIRA",
            "subtitle": "Flutter + Django + IA",
            "description": (
                "Application intelligente destinée à accompagner "
                "les utilisateurs dans leurs démarches et leur "
                "développement professionnel."
            ),
        }
    ],

    "certifications": [
        "Formation DevOps & Cloud",
        "Formation Flutter",
    ],
}


templates = [
    "classic",
    "modern",
    "minimal",
    "elegant",
    "tech",
    "student",
]


for template in templates:

    cv = SimpleNamespace(
        full_name="Hassimiou Diallo",
        email="hassimiou@example.com",
        phone="+224 000 00 00 00",
        summary=(
            "Développeur passionné par l'intelligence artificielle, "
            "le développement d'applications, la cybersécurité, "
            "le DevOps et le Cloud."
        ),
        template=template,
        data=data,
    )

    pdf = generate_pdf(cv)

    filename = f"test_pdfs/cv_{template}.pdf"

    with open(filename, "wb") as file:
        file.write(pdf)

    print(
        f"OK : {filename} - {len(pdf)} octets"
    )


print()
print("====================================")
print("LES 6 PDF ONT ÉTÉ GÉNÉRÉS")
print("====================================")