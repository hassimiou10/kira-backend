# Module Education

Ce module gère les enregistrements de formation pour les utilisateurs.

## Endpoints disponibles

- Liste / création : `GET` / `POST` `/api/education/records/`
- Détail : `GET` / `PUT` / `PATCH` / `DELETE` `/api/education/records/{id}/`
- Recherche : `GET` `/api/education/search/?q=<terme>`

## Filtres disponibles

- `institution`, `degree`, `field_of_study`
  - `exact`
  - `icontains`
- `is_current`
  - `exact`
- `start_date`, `end_date`
  - `exact`
  - `gte`
  - `lte`
- `ordering`
  - `start_date`, `end_date`, `created_at`, `updated_at`, `institution`

## Exemple d’utilisation

Rechercher des formations contenant `Backend` :

```http
GET /api/education/search/?q=Backend
Authorization: Bearer <token>
```

Obtenir les enregistrements triés par date de fin la plus récente :

```http
GET /api/education/records/?ordering=-end_date
Authorization: Bearer <token>
```

Filtrer les formations en cours :

```http
GET /api/education/records/?is_current=True
Authorization: Bearer <token>
```

## Validation

Lancer les tests du module :

```powershell
python manage.py test education
```
