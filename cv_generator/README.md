# CV Generator Backend

This Django app provides a backend for creating, updating, deleting, and generating CVs (resumes).

## Features

- CRUD operations for `CV` objects
- PDF generation using either `reportlab` (default) or `weasyprint`
- AI integration placeholder for resume suggestion generation
- Friendly PDF download endpoint with `Content-Disposition`

## Models

- `CV`
  - `owner`: reference to authenticated user
  - `full_name`, `email`, `phone`, `summary`
  - `data`: JSON field for experience, education, skills, projects, certifications
  - `pdf`: binary field storing the last generated PDF

## `data` format

The `data` field is a free-form JSON object for structured resume sections. The current PDF generator and AI hooks expect sections like:

```json
{
  "experience": [
    {
      "title": "Backend Developer",
      "subtitle": "Acme Corp · 2022 - Present",
      "description": "Built APIs in Django and managed PostgreSQL databases."
    }
  ],
  "education": [
    {
      "title": "M.S. Computer Science",
      "subtitle": "University Name · 2020",
      "description": "Focus on software engineering and data systems."
    }
  ],
  "skills": ["Python", "Django", "REST", "PostgreSQL"],
  "projects": [
    {
      "title": "CV Generator",
      "subtitle": "Personal project",
      "description": "A Django backend that creates and exports CVs as PDF."
    }
  ],
  "certifications": [
    {
      "title": "AWS Certified Developer",
      "subtitle": "2024"
    }
  ]
}
```

All keys are optional and may be omitted or extended with additional sections. The PDF renderer currently supports the standard sections above.

## API Endpoints

Assuming `config/urls.py` includes `path('api/cv/', include('cv_generator.urls'))`:

- `GET /api/cv/cvs/`
- `POST /api/cv/cvs/`
- `GET /api/cv/cvs/{id}/`
- `PATCH /api/cv/cvs/{id}/`
- `DELETE /api/cv/cvs/{id}/`
- `GET /api/cv/cvs/{id}/pdf/`
- `GET /api/cv/cvs/{id}/download_pdf/`
- `POST /api/cv/cvs/{id}/ai_generate/`

## Example create request

```bash
curl -X POST https://your-api.example.com/api/cv/cvs/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "phone": "+33 6 12 34 56 78",
    "summary": "Backend developer with 5+ years of experience in Django and APIs.",
    "data": {
      "experience": [
        {
          "title": "Senior Backend Developer",
          "subtitle": "Acme Corp · 2023 - Present",
          "description": "Designed REST APIs and managed PostgreSQL deployments."
        }
      ],
      "education": [
        {
          "title": "Master in Computer Science",
          "subtitle": "Université de Paris · 2022",
          "description": "Specialized in software architecture and data engineering."
        }
      ],
      "skills": ["Python", "Django", "REST", "PostgreSQL"]
    }
  }'
```

## Configuration

In `config/settings.py`:

- `CV_PDF_BACKEND = 'reportlab'` or `'weasy'`
- `OPENAI_API_KEY` enables OpenAI-based AI suggestions
- `AI_MODEL_DEFAULT` sets the default model name

In `.env.example`:

- `CV_PDF_BACKEND=reportlab`
- `OPENAI_API_KEY=sk-your-openai-key`
- `GEMINI_API_KEY=your-gemini-key`
- `AI_MODEL_DEFAULT=gpt-4o-mini`

## Download PDF example

```bash
curl -L -H "Authorization: Bearer <token>" \
  https://your-api.example.com/api/cv/cvs/1/download_pdf/ \
  -o jean_dupont_1.pdf
```

## Update request example

```bash
curl -X PATCH https://your-api.example.com/api/cv/cvs/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Updated backend developer summary",
    "data": {
      "skills": ["Python", "Django", "APIs", "PostgreSQL"]
    }
  }'
```

## AI generate request example

```bash
curl -X POST https://your-api.example.com/api/cv/cvs/1/ai_generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Propose a concise professional summary for this CV"
  }'
```

## Tests

Run the module tests with:

```bash
python manage.py test cv_generator
```
