from google import genai

client = genai.Client(api_key=GOOGLE_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello! Confirming the connection is successful.",
)
print(response.text)