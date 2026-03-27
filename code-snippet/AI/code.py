from openai import OpenAI

endpoint = "https://af-hackrva.openai.azure.com/openai/v1/"
deployment_name = "gpt-5.4-mini"
api_key = "<your-api-key>"

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(completion.choices[0].message)