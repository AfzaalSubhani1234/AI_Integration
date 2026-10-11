
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from function import calculator, get_weather


# Step 1: Load API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env")

# Step 2: Create Gemini client
client = genai.Client(api_key=api_key)


# Step 3: Configure Gemini
config = types.GenerateContentConfig(
    system_instruction=(
        "You are a helpful AI assistant. "
        "Use calculator for mathematical calculations. "
        "For calculator, provide operation, a, and b. "
        "Operations: add, subtract, multiply, divide. "
        "Use get_weather for current weather questions. "
        "Ask for a city if it is missing. "
        "Explain function results clearly."
    ),
    tools=[calculator, get_weather],
    temperature=0.7,
    max_output_tokens=500,
)


# Step 4: Store conversation history
history = []


# Step 5: Chat loop
while True:
    question = input("\nYou (type exit to stop): ").strip()

    if question.lower() == "exit":
        print("Chat ended!")
        break

    if not question:
        print("Please enter a question.")
        continue

    history.append(
        types.Content(
            role="user",
            parts=[types.Part(text=question)],
        )
    )

    try:
        # Step 6: Stream Gemini's response
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=history,
            config=config,
        )

        response_parts = []

        print("\nGemini: ", end="", flush=True)

        for chunk in response:
            if not chunk.candidates:
                continue

            candidate = chunk.candidates[0]

            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    response_parts.append(part)

                    if part.text:
                        print(part.text, end="", flush=True)

        print()

        # Save Gemini's complete response
        if response_parts:
            history.append(
                types.Content(
                    role="model",
                    parts=response_parts,
                )
            )

        # Step 7: Find function calls
        function_calls = [
            part
            for part in response_parts
            if part.function_call
        ]

        if not function_calls:
            continue

        # Step 8: Execute the requested Python functions
        function_responses = []

        for part in function_calls:
            function_call = part.function_call
            name = function_call.name
            args = dict(function_call.args)

            print(f"[Calling function: {name}]")

            if name == "calculator":
                result = calculator(**args)

            elif name == "get_weather":
                result = get_weather(**args)

            else:
                result = f"Unknown function: {name}"

            function_responses.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": result},
                    id=function_call.id,
                )
            )

        # Step 9: Send function results back to Gemini
        history.append(
            types.Content(
                role="user",
                parts=function_responses,
            )
        )

        follow_up = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=history,
            config=config,
        )

        follow_up_parts = []

        print("\nGemini: ", end="", flush=True)

        for chunk in follow_up:
            if not chunk.candidates:
                continue

            candidate = chunk.candidates[0]

            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    follow_up_parts.append(part)

                    if part.text:
                        print(part.text, end="", flush=True)

        print()

        if follow_up_parts:
            history.append(
                types.Content(
                    role="model",
                    parts=follow_up_parts,
                )
            )

    except Exception as error:
        print(f"\nError: {error}")
