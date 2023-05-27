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
        if(len(sample_rows) <= 10):
            sample_rows.append(row)

sample_rows_string = ""
for row in sample_rows:
    sample_rows_string += ','.join(row)


datasource_start_prompt = f"""
Using this sample input data, generate Python code that maps to this schema.
Use the name without extension {file_name} + year for the datasource_id
""" + sample_rows_string + '\n' + datasource_schema

actor_start_prompt = f"""
    Now generate the python code to map to actor schema
""" + actor_schema

values = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
      {"role": "system", "content": datasource_start_prompt},
      # {"role": "system", "content": actor_start_prompt}
    ]
)
print(values)