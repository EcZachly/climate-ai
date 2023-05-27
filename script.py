import openai
import csv
import os
from schema.schemas import actor_schema, emissions_agg, datasource_schema
openai.api_key = os.environ.get("OPENAI_KEY")


# file_name = '2016_-_Citywide_GHG_Emissions.csv'
file_name = '2020_-_Full_States_and_Regions_Dataset.csv'


sample_rows = []
with open('data/' + file_name, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if(len(sample_rows) <= 2):
            sample_rows.append(row)

sample_rows_string = ""
for row in sample_rows:
    sample_rows_string += ','.join(row)


start_prompt = f"""
Using this sample input data, generate Python code in markdown that maps to this schema.
Use the name without extension {file_name} + year for the datasource_id
""" + sample_rows_string

datasource_start_prompt = f"""
Using this sample input data, generate Python code that maps to this schema.
Use the name without extension {file_name} + year for the datasource_id
""" + sample_rows_string



values = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
      {"role": "system", "content": start_prompt + ' ' + datasource_schema + " output to a file named datasource.csv"}
      # {"role": "system", "content": start_prompt + ' ' + actor_schema + " output to a file named actors.csv"}
    ]
)


output_message = values["choices"][0]["message"]["content"].split('```')

print(output_message)
valid_messages = filter(lambda x: x.startswith('python'), output_message)
valid_messages = map(lambda x: x[6:], valid_messages)


# Open the file with write permissions
with open('output/' + file_name + '.py', 'w') as file:
    # Write some data to the file
    file.write('\n'.join(valid_messages))
