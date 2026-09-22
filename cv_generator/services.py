"""
Services de génération de CV.

Gère :
- Génération PDF
- 6 templates CV
- Génération IA
- Amélioration IA
"""

import io
import json
import os
import logging

logger = logging.getLogger(__name__)


CV_TEMPLATES = [
    "classic",
    "modern",
    "minimal",
    "elegant",
    "tech",
    "student",
]


def _draw_wrapped_text(
    p,
    x,
    y,
    text,
    max_width,
    leading=12,
    font_name="Helvetica",
    font_size=10,
):
    """Écrit automatiquement un texte sur plusieurs lignes."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    text = str(text or "").strip()

    if not text:
        return p.beginText(x, y)

    p.setFont(font_name, font_size)

    words = text.split()
    line = ""

    text_obj = p.beginText(x, y)
    text_obj.setLeading(leading)

    for word in words:
        test = (line + " " + word).strip()

        if stringWidth(
            test,
            font_name,
            font_size,
        ) <= max_width:
            line = test
        else:
            if line:
                text_obj.textLine(line)
            line = word

    if line:
        text_obj.textLine(line)

    return text_obj


def _draw_section_title(
    p,
    title,
    x,
    y,
    color,
):
    """Dessine un titre de section."""
    from reportlab.pdfbase.pdfmetrics import stringWidth

    p.setFillColor(color)
    p.setFont("Helvetica-Bold", 11)

    p.drawString(
        x,
        y,
        title.upper(),
    )

    line_width = stringWidth(
        title.upper(),
        "Helvetica-Bold",
        11,
    )

    p.setStrokeColor(color)
    p.setLineWidth(1)

    p.line(
        x,
        y - 3,
        x + line_width,
        y - 3,
    )

    return y - 20


def _draw_items(
    p,
    items,
    x,
    y,
    max_width,
    font_size=9,
    color=None,
):
    """Dessine une liste de données."""
    from reportlab.lib import colors

    if color is None:
        color = colors.black

    p.setFillColor(color)

    for item in items or []:
        if isinstance(item, dict):
            title = (
                item.get("title")
                or item.get("name")
                or item.get("role")
                or ""
            )

            subtitle = (
                item.get("subtitle")
                or item.get("company")
                or item.get("school")
                or ""
            )

            description = (
                item.get("description")
                or item.get("details")
                or ""
            )

            if title:
                p.setFont(
                    "Helvetica-Bold",
                    font_size,
                )

                p.drawString(
                    x,
                    y,
                    str(title)[:100],
                )

                y -= 13

            if subtitle:
                p.setFont(
                    "Helvetica-Oblique",
                    font_size - 1,
                )

                p.drawString(
                    x,
                    y,
                    str(subtitle)[:100],
                )

                y -= 12

            if description:
                text_obj = _draw_wrapped_text(
                    p,
                    x,
                    y,
                    description,
                    max_width,
                    leading=11,
                    font_name="Helvetica",
                    font_size=font_size,
                )

                p.drawText(text_obj)

                y = text_obj.getY() - 7

        else:
            text_obj = _draw_wrapped_text(
                p,
                x,
                y,
                f"• {item}",
                max_width,
                leading=11,
                font_name="Helvetica",
                font_size=font_size,
            )

            p.drawText(text_obj)

            y = text_obj.getY() - 5

        if y < 70:
            p.showPage()
            y = 780

    return y


def _get_cv_data(cv):
    data = getattr(cv, "data", None)

    if not isinstance(data, dict):
        data = {}

    return data


def _get_template(cv):
    template = getattr(
        cv,
        "template",
        "modern",
    )

    if template not in CV_TEMPLATES:
        return "modern"

    return template


# ============================================================
# PHOTO
# ============================================================

def _draw_cv_photo(
    p,
    cv,
    x,
    y,
    size=90,
    border=True,
):
    """
    Dessine la photo du CV dans le PDF.

    x, y = coin inférieur gauche de la photo.
    size = largeur/hauteur maximale de la photo.
    """

    photo = getattr(cv, "photo", None)

    if not photo:
        return False

    try:
        from reportlab.lib.utils import ImageReader

        # Ouvre le fichier stocké par Django
        photo.open("rb")

        image = ImageReader(photo.file)

        # Cadre autour de la photo
        if border:
            from reportlab.lib import colors

            p.setStrokeColor(colors.white)
            p.setLineWidth(2)

            p.rect(
                x - 2,
                y - 2,
                size + 4,
                size + 4,
                fill=0,
                stroke=1,
            )

        # Dessin de la photo
        p.drawImage(
            image,
            x,
            y,
            width=size,
            height=size,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )

        photo.close()

        logger.info(
            "Photo ajoutée au PDF pour le CV %s",
            getattr(cv, "id", "inconnu"),
        )

        return True

    except Exception as exc:
        logger.exception(
            "Impossible d'ajouter la photo au PDF : %s",
            exc,
        )

        try:
            photo.close()
        except Exception:
            pass

        return False


# ============================================================
# TEMPLATE CLASSIC
# ============================================================

def _generate_classic_pdf(
    cv,
    p,
    width,
    height,
):
    from reportlab.lib import colors

    margin = 45
    y = height - 50

    # Photo en haut à droite
    photo_size = 90

    has_photo = _draw_cv_photo(
        p,
        cv,
        width - margin - photo_size,
        height - 140,
        size=photo_size,
        border=True,
    )

    # Nom
    p.setFillColor(colors.black)
    p.setFont(
        "Helvetica-Bold",
        22,
    )

    p.drawString(
        margin,
        y,
        cv.full_name or "",
    )

    y -= 25

    # Poste
    data = _get_cv_data(cv)

    job_title = data.get(
        "job_title",
        "",
    )

    if job_title:
        p.setFont(
            "Helvetica",
            11,
        )

        p.drawString(
            margin,
            y,
            job_title,
        )

        y -= 18

    # Contact
    contact = []

    if getattr(cv, "email", None):
        contact.append(cv.email)

    if getattr(cv, "phone", None):
        contact.append(cv.phone)

    if contact:
        p.setFont(
            "Helvetica",
            9,
        )

        p.drawString(
            margin,
            y,
            " | ".join(contact),
        )

        y -= 25

    # Si photo présente, on laisse de l'espace sous l'en-tête
    if has_photo:
        y = min(
            y,
            height - 165,
        )

    # Profil
    if cv.summary:
        y = _draw_section_title(
            p,
            "Profil",
            margin,
            y,
            colors.black,
        )

        text = _draw_wrapped_text(
            p,
            margin,
            y,
            cv.summary,
            width - 2 * margin,
        )

        p.drawText(text)

        y = text.getY() - 18

    # Sections
    sections = [
        ("Expérience", "experience"),
        ("Formation", "education"),
        ("Projets", "projects"),
        ("Compétences", "skills"),
        ("Certifications", "certifications"),
    ]

    for title, key in sections:
        items = data.get(key) or []

        if not items:
            continue

        y = _draw_section_title(
            p,
            title,
            margin,
            y,
            colors.black,
        )

        y = _draw_items(
            p,
            items,
            margin,
            y,
            width - 2 * margin,
        )

        y -= 8


# ============================================================
# TEMPLATE MODERN
# ============================================================

def _generate_modern_pdf(
    cv,
    p,
    width,
    height,
):
    from reportlab.lib import colors

    sidebar_width = 155

    # Colonne gauche
    p.setFillColor(
        colors.HexColor("#172554")
    )

    p.rect(
        0,
        0,
        sidebar_width,
        height,
        fill=1,
        stroke=0,
    )

    # Photo
    photo_size = 90

    _draw_cv_photo(
        p,
        cv,
        32,
        height - 145,
        size=photo_size,
        border=True,
    )

    # Nom
    p.setFillColor(colors.white)

    p.setFont(
        "Helvetica-Bold",
        15,
    )

    p.drawString(
        25,
        height - 165,
        cv.full_name or "",
    )

    # Contact
    y_left = height - 190

    p.setFont(
        "Helvetica",
        8,
    )

    if cv.email:
        p.drawString(
            25,
            y_left,
            cv.email[:25],
        )

        y_left -= 16

    if cv.phone:
        p.drawString(
            25,
            y_left,
            cv.phone,
        )

    # Contenu principal
    x = sidebar_width + 30
    y = height - 55

    data = _get_cv_data(cv)

    job_title = data.get(
        "job_title",
        "",
    )

    if job_title:
        p.setFillColor(colors.black)

        p.setFont(
            "Helvetica-Bold",
            18,
        )

        p.drawString(
            x,
            y,
            job_title,
        )

        y -= 30

    if cv.summary:
        y = _draw_section_title(
            p,
            "Profil",
            x,
            y,
            colors.HexColor("#172554"),
        )

        text = _draw_wrapped_text(
            p,
            x,
            y,
            cv.summary,
            width - x - 35,
        )

        p.drawText(text)

        y = text.getY() - 20

    sections = [
        ("Expérience", "experience"),
        ("Formation", "education"),
        ("Projets", "projects"),
        ("Compétences", "skills"),
    ]

    for title, key in sections:
        items = data.get(key) or []

        if not items:
            continue

        y = _draw_section_title(
            p,
            title,
            x,
            y,
            colors.HexColor("#172554"),
        )

        y = _draw_items(
            p,
            items,
            x,
            y,
            width - x - 35,
        )

        y -= 8


# ============================================================
# TEMPLATE MINIMAL
# ============================================================

def _generate_minimal_pdf(
    cv,
    p,
    width,
    height,
):
    from reportlab.lib import colors

    margin = 55
    y = height - 55

    # Photo en haut à droite
    photo_size = 85

    has_photo = _draw_cv_photo(
        p,
        cv,
        width - margin - photo_size,
        height - 135,
        size=photo_size,
        border=True,
    )

    p.setFillColor(colors.black)

    p.setFont(
        "Helvetica-Bold",
        25,
    )

    p.drawString(
        margin,
        y,
        cv.full_name or "",
    )

    y -= 18

    p.setStrokeColor(
        colors.black
    )

    p.line(
        margin,
        y,
        width - margin,
        y,
    )

    y -= 25

    data = _get_cv_data(cv)

    job_title = data.get(
        "job_title",
        "",
    )

    if job_title:
        p.setFont(
            "Helvetica",
            11,
        )

        p.drawString(
            margin,
            y,
            job_title,
        )

        y -= 25

    if has_photo:
        y = min(
            y,
            height - 155,
        )

    if cv.summary:
        p.setFont(
            "Helvetica-Bold",
            10,
        )

        p.drawString(
            margin,
            y,
            "PROFIL",
        )

        y -= 15

        text = _draw_wrapped_text(
            p,
            margin,
            y,
            cv.summary,
            width - 2 * margin,
            font_size=9,
        )

        p.drawText(text)

        y = text.getY() - 20

    sections = [
        ("EXPÉRIENCE", "experience"),
        ("FORMATION", "education"),
        ("PROJETS", "projects"),
        ("COMPÉTENCES", "skills"),
    ]

    for title, key in sections:
        items = data.get(key) or []

        if not items:
            continue

        p.setFont(
            "Helvetica-Bold",
            10,
        )

        p.drawString(
            margin,
            y,
            title,
        )

        y -= 17

        y = _draw_items(
            p,
            items,
            margin,
            y,
            width - 2 * margin,
            font_size=9,
        )

        y -= 8


# ============================================================
# TEMPLATE ELEGANT
# ============================================================

def _generate_elegant_pdf(
    cv,
    p,
    width,
    height,
):
    from reportlab.lib import colors

    margin = 50
    y = height - 55

    gold = colors.HexColor(
        "#9A7B2F"
    )

    # Photo centrée en haut
    photo_size = 80

    has_photo = _draw_cv_photo(
        p,
        cv,
        (width - photo_size) / 2,
        height - 145,
        size=photo_size,
        border=True,
    )

    # Nom
    p.setFillColor(gold)

    p.setFont(
        "Helvetica-Bold",
        24,
    )

    p.drawCentredString(
        width / 2,
        y,
        cv.full_name or "",
    )

    y -= 20

    data = _get_cv_data(cv)

    job_title = data.get(
        "job_title",
        "",
    )

    if job_title:
        p.setFillColor(colors.black)

        p.setFont(
            "Helvetica-Oblique",
            11,
        )

        p.drawCentredString(
            width / 2,
            y,
            job_title,
        )

        y -= 20

    p.setStrokeColor(gold)

    p.setLineWidth(1.5)

    p.line(
        margin,
        y,
        width - margin,
        y,
    )

    y -= 25

    if has_photo:
        y = min(
            y,
            height - 175,
        )

    if cv.summary:
        y = _draw_section_title(
            p,
            "Profil",
            margin,
            y,
            gold,
        )

        text = _draw_wrapped_text(
            p,
            margin,
            y,
            cv.summary,
            width - 2 * margin,
            font_size=9,
        )

        p.drawText(text)

        y = text.getY() - 20

    sections = [
        (
            "Expérience professionnelle",
            "experience",
        ),
        ("Formation", "education"),
        ("Projets", "projects"),
        ("Compétences", "skills"),
        ("Certifications", "certifications"),
    ]

    for title, key in sections:
        items = data.get(key) or []

        if not items:
            continue

        y = _draw_section_title(
            p,
            title,
            margin,
            y,
            gold,
        )

        y = _draw_items(
            p,
            items,
            margin,
            y,
            width - 2 * margin,
            font_size=9,
        )

        y -= 8


# ============================================================
# TEMPLATE TECH
# ============================================================

def _generate_tech_pdf(
    cv,
    p,
    width,
    height,
):
    from reportlab.lib import colors

    margin = 40

    y = height - 45

    blue = colors.HexColor(
        "#0EA5E9"
    )

    dark = colors.HexColor(
        "#0F172A"
    )

    # Header
    p.setFillColor(dark)

    p.rect(
        0,
        height - 120,
        width,
        120,
        fill=1,
        stroke=0,
    )

    # Photo à droite du header
    photo_size = 75

    _draw_cv_photo(
        p,
        cv,
        width - margin - photo_size,
        height - 105,
        size=photo_size,
        border=True,
    )

    # Nom
    p.setFillColor(blue)

    p.setFont(
        "Helvetica-Bold",
        21,
    )

    p.drawString(
        margin,
        height - 55,
        cv.full_name or "",
    )

    data = _get_cv_data(cv)

    job_title = data.get(
        "job_title",
        "Software Developer",
    )

    p.setFont(
        "Helvetica",
        11,
    )

    p.drawString(
        margin,
        height - 78,
        job_title,
    )

    p.setFillColor(colors.black)

    y = height - 145

    # Résumé
    if cv.summary:
        y = _draw_section_title(
            p,
            "About",
            margin,
            y,
            blue,
        )

        text = _draw_wrapped_text(
            p,
            margin,
            y,
            cv.summary,
            width - 2 * margin,
            font_size=9,
        )

        p.drawText(text)

        y = text.getY() - 20

    sections = [
        ("Skills", "skills"),
        ("Experience", "experience"),
        ("Projects", "projects"),
        ("Education", "education"),
        ("Certifications", "certifications"),
    ]

    for title, key in sections:
        items = data.get(key) or []

        if not items:
            continue

        y = _draw_section_title(
            p,
            title,
            margin,
            y,
            blue,
        )

        y = _draw_items(
            p,
            items,
            margin,
            y,
            width - 2 * margin,
            font_size=9,
        )

        y -= 8


# ============================================================
# TEMPLATE STUDENT
# ============================================================

def _generate_student_pdf(
    cv,
    p,
    width,
    height,
):
    from reportlab.lib import colors

    margin = 45
    y = height - 45

    green = colors.HexColor(
        "#16A34A"
    )

    # Header
    p.setFillColor(green)

    p.rect(
        0,
        height - 105,
        width,
        105,
        fill=1,
        stroke=0,
    )

    # Photo à droite
    photo_size = 70

    _draw_cv_photo(
        p,
        cv,
        width - margin - photo_size,
        height - 95,
        size=photo_size,
        border=True,
    )

    # Nom
    p.setFillColor(colors.white)

    p.setFont(
        "Helvetica-Bold",
        21,
    )

    p.drawString(
        margin,
        height - 50,
        cv.full_name or "",
    )

    data = _get_cv_data(cv)

    job_title = data.get(
        "job_title",
        "Étudiant / Jeune diplômé",
    )

    p.setFont(
        "Helvetica",
        10,
    )

    p.drawString(
        margin,
        height - 72,
        job_title,
    )

    y = height - 135

    # Profil
    if cv.summary:
        y = _draw_section_title(
            p,
            "Profil",
            margin,
            y,
            green,
        )

        text = _draw_wrapped_text(
            p,
            margin,
            y,
            cv.summary,
            width - 2 * margin,
            font_size=9,
        )

        p.drawText(text)

        y = text.getY() - 20

    sections = [
        ("Formation", "education"),
        ("Projets", "projects"),
        ("Compétences", "skills"),
        ("Expérience", "experience"),
        ("Certifications", "certifications"),
    ]

    for title, key in sections:
        items = data.get(key) or []

        if not items:
            continue

        y = _draw_section_title(
            p,
            title,
            margin,
            y,
            green,
        )

        y = _draw_items(
            p,
            items,
            margin,
            y,
            width - 2 * margin,
            font_size=9,
        )

        y -= 8


# ============================================================
# GENERATION PDF PRINCIPALE
# ============================================================

def generate_pdf(cv):
    """
    Génère le PDF en fonction du template sélectionné.

    Templates :
    classic
    modern
    minimal
    elegant
    tech
    student
    """

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as exc:
        raise RuntimeError(
            "ReportLab est nécessaire. "
            "Installez-le avec : pip install reportlab"
        ) from exc

    buffer = io.BytesIO()

    width, height = A4

    p = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    template = _get_template(cv)

    if template == "classic":
        _generate_classic_pdf(
            cv,
            p,
            width,
            height,
        )

    elif template == "modern":
        _generate_modern_pdf(
            cv,
            p,
            width,
            height,
        )

    elif template == "minimal":
        _generate_minimal_pdf(
            cv,
            p,
            width,
            height,
        )

    elif template == "elegant":
        _generate_elegant_pdf(
            cv,
            p,
            width,
            height,
        )

    elif template == "tech":
        _generate_tech_pdf(
            cv,
            p,
            width,
            height,
        )

    elif template == "student":
        _generate_student_pdf(
            cv,
            p,
            width,
            height,
        )

    else:
        _generate_modern_pdf(
            cv,
            p,
            width,
            height,
        )

    p.showPage()
    p.save()

    pdf = buffer.getvalue()

    buffer.close()

    return pdf


# ============================================================
# IA - GENERATION DE RESUME
# ============================================================

def ai_generate_resume(
    data,
    prompt=None,
):
    """
    Génère des suggestions structurées avec OpenAI.
    """

    openai_api_key = os.environ.get(
        "OPENAI_API_KEY"
    )

    if openai_api_key:
        try:
            import openai

            openai.api_key = openai_api_key

            system = (
                "You are an assistant that outputs a JSON object "
                "describing resume sections: experience, education, "
                "skills, projects, certifications and summary. "
                "Respond with only valid JSON."
            )

            user_prompt = (
                "Existing data:\n"
                + json.dumps(
                    data or {},
                    ensure_ascii=False,
                )
                + "\n\n"
            )

            if prompt:
                user_prompt += (
                    "Instruction: "
                    + prompt
                )

            response = openai.ChatCompletion.create(
                model=os.environ.get(
                    "OPENAI_MODEL",
                    "gpt-4o-mini",
                ),
                messages=[
                    {
                        "role": "system",
                        "content": system,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=1200,
            )

            text = response[
                "choices"
            ][0][
                "message"
            ][
                "content"
            ].strip()

            try:
                parsed = json.loads(text)

                if isinstance(
                    parsed,
                    dict,
                ):
                    return parsed

            except Exception:
                import re

                # Recherche d'un objet JSON dans la réponse
                match = re.search(
                    r"\{.*\}",
                    text,
                    re.S,
                )

                if match:
                    try:
                        parsed = json.loads(
                            match.group(0)
                        )

                        if isinstance(
                            parsed,
                            dict,
                        ):
                            return parsed

                    except Exception:
                        logger.exception(
                            "Impossible de parser la réponse IA."
                        )

        except Exception:
            logger.exception(
                "Erreur lors de l'appel OpenAI."
            )

    fallback = {}

    if data is None:
        data = {}

    if not data.get("summary"):
        sample_summary = None

        if prompt:
            sample_summary = prompt.strip()

        elif data.get("experience"):
            first = data.get(
                "experience"
            )[0]

            if isinstance(
                first,
                dict,
            ):
                sample_summary = (
                    f"Professionnel avec expérience en "
                    f"{first.get('title', 'développement')}"
                )

            else:
                sample_summary = str(
                    first
                )[:200]

        if sample_summary:
            fallback[
                "summary"
            ] = sample_summary

    if not data.get("skills"):
        fallback[
            "skills"
        ] = []

    return fallback


# ============================================================
# GENERATION COMPLETE DU CV
# ============================================================

def generate_full_cv_from_description(
    description,
):
    """
    Génère une structure complète de CV
    à partir d'une description utilisateur.
    """

    if not description:
        return {
            "error": "La description est obligatoire."
        }

    data = {
        "summary": description,
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
    }

    # Appel IA
    ai_result = ai_generate_resume(
        data=data,
        prompt=description,
    )

    if isinstance(
        ai_result,
        dict,
    ):
        data.update(
            ai_result
        )

    return data