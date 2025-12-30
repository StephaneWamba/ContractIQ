"""Test OpenAI connection and Instructor integration"""
import instructor
from openai import OpenAI
from src.core.config import settings
import os

print("=" * 60)
print("OpenAI Connection Test")
print("=" * 60)

# Check environment variables
print(f"\n1. Environment Check:")
print(f"   OPENAI_API_KEY from env: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"   OPENAI_API_KEY from settings: {'SET' if settings.OPENAI_API_KEY else 'NOT SET'}")
print(f"   OPENAI_MODEL: {settings.OPENAI_MODEL}")
print(f"   USE_LLM_FOR_EXTRACTION: {settings.USE_LLM_FOR_EXTRACTION}")

if not settings.OPENAI_API_KEY:
    print("\n❌ ERROR: OPENAI_API_KEY is not set!")
    print("   Please add OPENAI_API_KEY to your .env file or docker-compose.yml")
    exit(1)

# Test basic OpenAI client
print(f"\n2. Creating OpenAI client...")
try:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    print("   ✓ Client created successfully")
except Exception as e:
    print(f"   ✗ Failed to create client: {e}")
    exit(1)

# Test Instructor patch
print(f"\n3. Patching with Instructor...")
try:
    instructor_client = instructor.patch(client)
    print("   ✓ Instructor patch successful")
except Exception as e:
    print(f"   ✗ Instructor patch failed: {e}")
    exit(1)

# Test simple API call
print(f"\n4. Testing API call (simple chat)...")
try:
    response = instructor_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": "Say 'Hello, OpenAI!'"}],
        max_tokens=20
    )
    print(f"   ✓ API call successful!")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"   ✗ API call failed: {e}")
    exit(1)

# Test structured output with Pydantic
print(f"\n5. Testing structured output with Instructor...")
from pydantic import BaseModel, Field

class TestModel(BaseModel):
    """Test model for structured output"""
    message: str = Field(description="A greeting message")
    number: int = Field(description="A random number between 1 and 10")

try:
    structured_response = instructor_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        response_model=TestModel,
        messages=[{"role": "user", "content": "Return a greeting and a number between 1 and 10"}],
        max_tokens=50
    )
    print(f"   ✓ Structured output successful!")
    print(f"   Message: {structured_response.message}")
    print(f"   Number: {structured_response.number}")
    print(f"   Type: {type(structured_response)}")
except Exception as e:
    print(f"   ✗ Structured output failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! OpenAI and Instructor are working correctly.")
print("=" * 60)


