import openai
import csv
import os
from schema.schemas import actor_schema, actions_schema, emissions_agg_schema, datasource_schema, target_schema

openai.api_key = os.environ.get("OPENAI_KEY")

# file_name = '2016_-_Citywide_GHG_Emissions.csv'
file_name = '2020_-_Full_States_and_Regions_Dataset.csv'


sample_rows = []
with open('data/' + file_name, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if (len(sample_rows) <= 10):
            sample_rows.append(row)

sample_rows_string = ""
for row in sample_rows:
    sample_rows_string += ','.join(row)

start_prompt = f"""
Using this sample input data, generate Python code in markdown 
that reads in the file data/{file_name} and maps to this schema
Use the name without extension {file_name} + year for the datasource_id
Use the file name for the name field
Ignore any additional data that doesn't map easily to target schema
""" + sample_rows_string

additional_prompts = """

Query the api https://openclimate.openearth.dev/api/v1/search/actor with query parameter name to get actor_id. 
The response from the api looks like {
data: [ {actor_id:''} ]
}

"""
output_prompt = " output to a csv file with header named {}.csv"

prompts = {
    'DataSource': ' '.join([start_prompt, datasource_schema, output_prompt.format("datasource")]),
    'Actor': ' '.join([start_prompt, additional_prompts, actor_schema, output_prompt.format("actor")]),
    'EmissionsAgg': ' '.join([start_prompt, additional_prompts, emissions_agg_schema, output_prompt.format("emissions_agg")]),
    'Target': ' '.join([start_prompt, additional_prompts, target_schema, output_prompt.format("target")]),
    'Action': ' '.join([start_prompt, additional_prompts, actions_schema, output_prompt.format("action")]),
}

for (schema_name, prompt) in prompts.items():
    print('running for prompt: ' + schema_name)
    values = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data analyst looking to map data to a conformed schema."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096
    )
    output_message = values["choices"][0]["message"]["content"].split('```')
    print(output_message)
    valid_messages = filter(lambda x: x.startswith('python'), output_message)
    valid_messages = map(lambda x: x[6:], valid_messages)

    # Open the file with write permissions
    with open('output/' + file_name + '.' + schema_name +'.py', 'w') as file:
        # Write some data to the file
        file.write('\n'.join(valid_messages))
