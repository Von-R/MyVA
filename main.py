import openai
from selenium import webdriver

# Initialize the OpenAI API client
openai.api_key = "API KEY GOES HERE"
driver = webdriver.Chrome()

initial_context = """You are my valued virtual assistant. Your task is to help me interact with websites dynamically,
using Python and Selenium exclusively, 
and more generally to complete any possible task that can be done involving the internet.
This includes navigating to webpages, extracting information, and performing tasks on my behalf.
When providing instructions that should be executed by Selenium, please prepend the instruction with 'Selenium!'. 
For example, 'Selenium! driver.get("https://example.com")'."""

reminder_context = """Reminder: Complete the task on the internet. Use only Python and Selenium. Prepend Selenium! to 
                    "any Selenium instructions. For example, 'Selenium! driver.get("https://example.com")'.")"""

conversation_history = []


def generate_api_response(context, conversation_history):
    # Prepare the prompt by appending the conversation history to the initial context
    prompt = context + "\n" + "\n".join([f"{entry['role']}: {entry['content']}" for entry in conversation_history])

    # Call the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-002",  # You can use other engines
        prompt=prompt,
        max_tokens=100,  # Limit the response to 100 tokens
    )

    # Extract and return the generated text
    return response.choices[0].text.strip()


def execute_action_or_code(action_or_code):
    if action_or_code.startswith("Selenium!"):
        code_snippets = action_or_code.replace("Selenium! ", "").split("\n")
        for code_snippet in code_snippets:
            if code_snippet.strip():  # check if the line is not empty
                try:
                    exec(code_snippet)
                except Exception as e:
                    return f"An error occurred: {e}"
        return f"Successfully executed: {action_or_code}"
    else:
        return f"ChatGPT: {action_or_code}"


while True:
    # Get the user's command
    user_command = input("You: ")

    # Update the conversation history
    conversation_history.append({"role": "user", "content": user_command})

    # Generate the API response
    api_response = generate_api_response(initial_context, conversation_history)

    # Check if the response is in Python code
    while True:
        if api_response.startswith("Selenium!") and "driver." in api_response:
            execution_result = execute_action_or_code(api_response)
            break
        else:
            conversation_history.append({"role": "user", "content": "Please remember to provide Python code using "
                                                                    "'Selenium!' and 'driver.' commands. Please send "
                                                                    "correct code"})
            api_response = generate_api_response(initial_context, conversation_history)

    # Update the conversation history
    conversation_history.append({"role": "assistant", "content": api_response})
    conversation_history.append({"role": "system", "content": execution_result})

    # Display the assistant's response and the execution result
    print(execution_result)
