# restaurant-menu-fastapi
REST API dengan web token authentication dengan memanfaatkan FastAPI dan OAuth 2.0 (Python)
## Deployment Link
>restaurant-menu-fastapi-python.herokuapp.com
## Swagger UI
>restaurant-menu-fastapi-python.herokuapp.com/docs
## Cara Penggunaan
Lakukan autentikasi dengan login menggunakan username dan password yang sudah tersedia, atau lakukan sign up dengan username yang belum diambil. Kemudian lakukan perintah yang diinginkan
## API Endpoint
- `/` GET: Read root
- `/menu` GET: Read all menu
- `/menu` POST: Add menu
- `/menu/{item_id}` GET: Read menu berdasarkan item_id
- `/menu/{item_id}` PUT: Update menu berdasarkan item_id
- `/menu/{item_id}` DELETE: Delete menu berdasarkan item_id
- `/token` POST: Login for access token
- `/signup` POST: Create user 