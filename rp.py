import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from faker import Faker

fake = Faker()

num_resources = 15
num_programs = 5
resources = [fake.name() for _ in range(num_resources)]
programs = [fake.company() for _ in range(num_programs)]


def generate_random_data(resources, programs):
    data = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 15)
    for program_name in programs:
        res = random.randint(2, num_resources - 3)
        for resource_name in resources[:res]:
            for _ in range(random.randint(1, 5)):
                start = start_date + timedelta(
                    days=random.randint(0, (end_date - start_date).days)
                )
                end = start + timedelta(weeks=random.randint(4, 10))
                skill = random.choice([
                    'Python', 'SQL', 'Java', 'C++', 'Tableau'
                ])
                weeks = str((end - start).days / 7)
                data.append([
                    resource_name, program_name, skill, start, end, weeks
                ])

    df = pd.DataFrame(
        data, columns=['Resource', 'Task', 'Skill', 'Start', 'Finish', 'Weeks']
    )
    return df


df = generate_random_data(resources, programs)
df['Program'] = df['Task']
df['Task'] = df['Skill']

unique_resources = df['Task'].unique()
resource_color_map = {
    resource:
        px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
    for i, resource in enumerate(unique_resources)
}

fig = go.Figure()
fig = px.timeline(
    df,
    x_start="Start",
    x_end="Finish",
    y="Task",
    color="Task",
    text="Weeks",
    width=2000,
    height=1200,
    color_discrete_map=resource_color_map,
)
fig.update_xaxes()
fig.update_layout(barmode="group")
#fig.update_layout(xaxis_range=[df.Start.min(), df.Finish.max()])
fig.show()
