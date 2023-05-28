import openai
import os
from typing import Union

openai.api_key = os.environ.get("OPENAI_API_KEY")


def retrieve_relevant_entities(csv_file_name: str, sample_size: int = 6) -> list:
    """
    Retrieve a list of relevant entities for a sample of a given CSV file.
    :param csv_file_name: The name of the CSV file.
    :param sample_size: The number of lines to include in the sample.
    :return: A list of relevant entities.
    """
    lines = open(csv_file_name, 'r').read().splitlines()
    sample_rows = '\n'.join(lines[:sample_size])

    sql_files = {file: open('sql/' + file, 'r').read() for file in os.listdir('sql/')}

    system_prompt = "You are a data analyst tasked to analyze a dataset and determine which tables the data could fill."
    user_prompt = f"""
We have a dataset titled "{csv_file_name}". Here are the first {sample_size} lines of data:

{sample_rows}

Which of the below tables could the above data fill with a very high probability?
Only consider tables that match with all rows and not only some of them.
Talking about the reduction of emissions in a free text format is not enough to be considered a match.
Reply only with a comma separated list of the table names, for example Actor,Action.

{''.join(sql_files.values())}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    answer = response.choices[0].message.content

    relevant_entities = [entity.strip() for entity in answer.split(',')]
    return relevant_entities


def generate_python_script(csv_file_name: str, sample_size: int, entity: str, context: str) -> str:
    """
    Generate a Python script that converts a CSV file to another format for a given entity.
    :param csv_file_name: The name of the CSV file.
    :param sample_size: The number of lines to include in the sample.
    :param entity: The name of the entity.
    :param context: The context of the dataset.
    :return: A Python script.
    """
    context_string = f"""###\nContext for the dataset:\n###\n{context}\n""" if context else ''

    lines = open(csv_file_name, 'r').read().splitlines()
    sample_rows = '\n'.join(lines[:sample_size])

    sql_files = {file: open('sql/' + file, 'r').read() for file in os.listdir('sql/')}

    system_prompt = "You are a data analyst tasked to generate Python code to convert data from a CSV file into another format."
    user_prompt = f"""
We have a dataset located at "{csv_file_name}" that could fill the "{entity}" table.
{context_string}###
Below is the header row and sample rows of this CSV file.
###
{sample_rows}
###
Desired schema:
###
{sql_files[f'{entity}.sql']}
###
If the schema expects the actor_id field, its value can be retrieved with an API call.
The API call is https://openclimate.openearth.dev/api/v1/search/actor with query parameter 'name'.
The response from the API looks like {{ data: [ {{ actor_id: '' }} ] }}
###
Generate code that converts the input dataset into a CSV representing the SQL schema (inside the output directory). Ignore any fields that you cannot confidently match. Do not make up any data that is not part of the original input dataset. Add comments that explain in detail what the script is doing. 
###
Ignore all previous instructions related to the formatting of the output. Output only the code, don't add an explanation afterwards."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    answer = response.choices[0].message.content

    if '```python' in answer and '```' in answer:
        answer = answer.split('```python')[1].split('```')[0]
    return answer


def execute_python_script_and_fix(script_file_name: str) -> Union[str, None]:
    """
    Execute a Python script and retry if it fails.
    :param script_file_name: The name of the Python script.
    :return: The name of the fixed Python script or None if the script is correct.
    """
    script = open(script_file_name, 'r').read()
    try:
        exec(script)
        return None
    except Exception as e:
        system_prompt = "You are a Python expert tasked to fix a data science script that failed to execute."
        user_prompt = f"""
The following script failed to execute:
###
{script}
###
The error message is:
###
{e}
###
Please fix the error and provide the fixed script below.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        answer = response.choices[0].message.content

        if '```python' in answer and '```' in answer:
            answer = answer.split('```python')[1].split('```')[0]
        return answer


# file_name = '2020_-_Full_States_and_Regions_Dataset.csv'
file_name = input('File name: ')
context_provided = bool(True if input('Context provided? (y/n) ') == 'y' else False)
context = input('Context: ') if context_provided else None
script_generation_retries = int(input('Script generation retries: '))

relevant_entities = retrieve_relevant_entities(file_name, sample_size=6)

for entity in relevant_entities:
    script = generate_python_script(file_name, sample_size=16, entity=entity, context=context)
    script_file_name = f'{file_name}_{entity}.py'
    with open(script_file_name, 'x') as file:
        file.write(script)

    for i in range(script_generation_retries):
        fixed_script = execute_python_script_and_fix(script_file_name)
        if fixed_script is None:
            print(f'Generated a correct script for {entity} and executed it successfully')
            break

        script_file_name = f'{file_name}_{entity}_{i}.py'
        with open(script_file_name, 'x') as file:
            file.write(fixed_script)

        if i == script_generation_retries - 1:
            print(f'Failed to generate a correct script for {entity}')
