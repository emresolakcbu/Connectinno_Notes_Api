import requests

# Firebase Project Web API Key (bunu senin projenin ayarlarından alacağız)
API_KEY = "AIzaSyA74gk_qNKWBWOl3t74FdF6Z8tCz8GA4m0"

# Firebase Authentication'da oluşturduğun test kullanıcı bilgisi
EMAIL = "test@test.com"
PASSWORD = "123456"

url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
payload = {
    "email": EMAIL,
    "password": PASSWORD,
    "returnSecureToken": True
}

resp = requests.post(url, json=payload)
print(resp.json())
