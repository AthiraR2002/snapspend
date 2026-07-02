from google import genai
client=genai.Client(api_key="AQ.Ab8RN6LqjsDjjwul0Zdre5cy4fcW2VLI6Aurt78D6bhsHoNu1w")
response=client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello Gemini"
)
print(response.text)