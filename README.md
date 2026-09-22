# Kira Backend

Projet Django REST pour la gestion de l'utilisateur, du CV et de l'éducation.

## Installation

1. Crée un environnement virtuel :
   ```powershell
   python -m venv env
   .\env\Scripts\Activate.ps1
   pip install -r requirements/development.txt
   ```
2. Configure les variables d'environnement dans un fichier `.env`.
3. Applique les migrations :
   ```powershell
   python manage.py migrate
   ```

## API Documentation

- JSON Schema : `/api/schema/`
- Swagger UI : `/api/schema/swagger-ui/`
- Redoc : `/api/schema/redoc/`

## Frontend Flutter

Le backend expose une API REST compatible avec Flutter. Utilise le JWT retourné par l’endpoint de login pour authentifier les requêtes.

Base URL typique : `http://localhost:8000`

### Authentification

- `POST /api/accounts/register/`
- `POST /api/accounts/login/`
- `POST /api/accounts/token/refresh/`

### Exemple de flux Flutter

1. Enregistrer un utilisateur :

```http
POST /api/accounts/register/
Content-Type: application/json

{
  "username": "user1",
  "email": "user1@example.com",
  "password": "pass1234"
}
```

2. Se connecter et récupérer le token :

```http
POST /api/accounts/login/
Content-Type: application/json

{
  "username": "user1",
  "password": "pass1234"
}
```

Réponse :

```json
{
  "access": "<ACCESS_TOKEN>",
  "refresh": "<REFRESH_TOKEN>"
}
```

3. Appeler une API protégée :

```http
GET /api/education/records/
Authorization: Bearer <ACCESS_TOKEN>
```

### Exemple Dart / Flutter

```dart
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

final storage = FlutterSecureStorage();
const baseUrl = 'http://localhost:8000';

Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/accounts/login/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'username': username, 'password': password}),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    await storeTokens(data['access'] as String, data['refresh'] as String);
    return data;
  }

  throw Exception('Erreur de connexion : ${response.body}');
}

Future<Map<String, dynamic>> register(String username, String email, String password) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/accounts/register/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'username': username, 'email': email, 'password': password}),
  );

  if (response.statusCode == 201) {
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  throw Exception('Erreur d\'inscription : ${response.body}');
}

Future<Map<String, dynamic>> refreshJwt(String refreshToken) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/accounts/token/refresh/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'refresh': refreshToken}),
  );

  if (response.statusCode == 200) {
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  throw Exception('Erreur de rafraîchissement de token : ${response.body}');
}

Future<void> storeTokens(String accessToken, String refreshToken) async {
  await storage.write(key: 'access_token', value: accessToken);
  await storage.write(key: 'refresh_token', value: refreshToken);
}

Future<Map<String, String?>> loadTokens() async {
  final accessToken = await storage.read(key: 'access_token');
  final refreshToken = await storage.read(key: 'refresh_token');
  return {'access': accessToken, 'refresh': refreshToken};
}

Future<void> clearTokens() async {
  await storage.delete(key: 'access_token');
  await storage.delete(key: 'refresh_token');
}

Future<http.Response> authorizedGet(String path) async {
  final tokens = await loadTokens();
  final accessToken = tokens['access'];
  final refreshToken = tokens['refresh'];

  if (accessToken == null || refreshToken == null) {
    throw Exception('Token manquant. Veuillez vous connecter.');
  }

  final response = await http.get(
    Uri.parse('$baseUrl$path'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
  );

  if (response.statusCode == 401) {
    final refreshed = await refreshJwt(refreshToken);
    await storeTokens(refreshed['access'] as String, refreshToken);
    return http.get(
      Uri.parse('$baseUrl$path'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${refreshed['access']}',
      },
    );
  }

  return response;
}

Future<http.Response> authorizedPost(String path, Map<String, dynamic> body) async {
  final tokens = await loadTokens();
  final accessToken = tokens['access'];
  final refreshToken = tokens['refresh'];

  if (accessToken == null || refreshToken == null) {
    throw Exception('Token manquant. Veuillez vous connecter.');
  }

  final response = await http.post(
    Uri.parse('$baseUrl$path'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $accessToken',
    },
    body: jsonEncode(body),
  );

  if (response.statusCode == 401) {
    final refreshed = await refreshJwt(refreshToken);
    await storeTokens(refreshed['access'] as String, refreshToken);
    return http.post(
      Uri.parse('$baseUrl$path'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${refreshed['access']}',
      },
      body: jsonEncode(body),
    );
  }

  return response;
}
```

### Packages Flutter recommandés

- `http`
- `flutter_secure_storage`

### CORS pour Flutter Web

Pour Flutter Web en développement, plusieurs origines locales sont autorisées par défaut :
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:8080`
- `http://127.0.0.1:8080`
- `http://localhost:5000`
- `http://127.0.0.1:5000`

Tu peux modifier `CORS_ALLOWED_ORIGINS` dans ton `.env` si ton app tourne sur une autre origine.

## Module Education

### Endpoints

- Liste et creation : `GET` / `POST` `/api/education/records/`
- Détail : `GET` / `PUT` / `PATCH` / `DELETE` `/api/education/records/{id}/`
- Recherche : `GET` `/api/education/search/?q=<terme>`

### Filtres disponibles

- `institution`, `degree`, `field_of_study` : `exact`, `icontains`
- `is_current` : `exact`
- `start_date`, `end_date` : `exact`, `gte`, `lte`
- `ordering` : `start_date`, `end_date`, `created_at`, `updated_at`, `institution`

### Exemples

Rechercher les formations contenant `Backend` :

```http
GET /api/education/search/?q=Backend
Authorization: Bearer <token>
```

Obtenir les enregistrements triés par date de fin la plus récente :

```http
GET /api/education/records/?ordering=-end_date
Authorization: Bearer <token>
```

Filtrer les diplômes en cours :

```http
GET /api/education/records/?is_current=True
Authorization: Bearer <token>
```

## Validation

Test unitaire du module éducation :

```powershell
python manage.py test education
```
