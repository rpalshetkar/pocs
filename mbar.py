import numpy as np
import plotly.graph_objects as go
from faker import Faker
from plotly.subplots import make_subplots

import pandas as pd

# Create a Faker instance
fake = Faker()

# Generate 40 resources and 8 projects
resources = [fake.name() for _ in range(40)]
projects = [fake.word() for _ in range(8)]
start_dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
start_dates = pd.DataFrame({
    'Start': start_dates
}).sample(40, replace=True)['Start']
end_dates = pd.DataFrame({
    'Start': start_dates
}).apply(
    lambda row: pd.date_range(start=row['Start'], end='2023-12-31', freq='D')
    [np.random.randint(
        0, len(pd.date_range(start=row['Start'], end='2023-12-31', freq='D'))
    )],
    axis=1
)

# Generate random effort within the start and end dates, ensuring resource doesn't work more than 48 weeks
effort = pd.DataFrame({
    'Start': start_dates,
    'End': end_dates
}).apply(
    lambda row: np.random.
    randint(1, 49, size=int((row['End'] - row['Start']).days + 1)),
    axis=1
)
repetition_factor = (len(projects) // len(resources) + 1)
resources_repeated = resources * repetition_factor
res = resources_repeated[:len(projects)]

df = pd.DataFrame({
    'Resource': res,
    'Project': projects * len(res),
    'Start': start_dates,
    'End': end_dates,
    'Effort': effort.values.flatten()
})


def create_subplot(df, key, field, group_by):
    fig = make_subplots(rows=len(df[key].unique()), cols=1, shared_xaxes=True)

    for i, name in enumerate(df[key].unique()):
        data = df[df[key] == name]
        x = pd.date_range(
            start=data['Start'].min(), end=data['End'].max(), freq='D'
        )
        y = data.groupby(pd.to_datetime(data['Start']).dt.to_period('D')
                         )[field].sum().reindex(x, fill_value=0)

        if group_by == 'Resource':
            fig.add_trace(
                go.Bar(x=x, y=y, name=data[group_by].unique()[0]),
                row=i + 1,
                col=1
            )
        elif group_by == 'Project':
            fig.add_trace(go.Bar(x=x, y=y, name=name), row=i + 1, col=1)

    fig.update_layout(
        title=f"{key} {field}", xaxis_title="Month", yaxis_title=field
    )
    fig.show()


# Example usage
create_subplot(df, 'Resource', 'Effort', 'Project')
