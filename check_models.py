from google import genai
from django.conf import settings
import os

# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

c = genai.Client(api_key=settings.GEMINI_API_KEY)

print("\nAVAILABLE MODELS:\n")
for m in c.models.list():
    print(m.name)