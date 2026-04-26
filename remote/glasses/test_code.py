import os
os.environ['GEMINI_API_KEY'] = 'YOUR_KEY'

from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Say hello"
)

print(response.text)