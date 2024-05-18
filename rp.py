import random
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
from faker import Faker

import pandas as pd


def gantt_chart(df, **kwargs):
    tick = 1
    y = kwargs.get('y', 'program')
    bar_col = kwargs.get('bars', y)
    start = kwargs.get('start', 'start')
    end = kwargs.get('end', 'end')
    measure = kwargs.get('measure', 'effort')

    columns = df.columns
    assert all(
        i in columns for i in [y, bar_col, start, end, measure]
    ), 'Mandatory columns missing, pass all of y, start, end, measure; bars optional'

    unique_bars = df[bar_col].unique()
    color_map = {
        resource:
            px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
        for i, resource in enumerate(unique_bars)
    }

    fig = go.Figure()
    fig = px.timeline(
        df,
        x_start=start,
        x_end=end,
        text=measure,
        y=y,
        color=bar_col,
        width=2000,
        height=1500,
        color_discrete_map=color_map,
    )
    fig.update_layout(
        barmode='group',
        plot_bgcolor='white',
        xaxis={'gridcolor': 'black'},
        yaxis={'gridcolor': 'black'},
    )
    fig.update_xaxes(dtick=f"M{tick}", tickformat='%b\n%Y')
    fig.update_layout(
        yaxis=dict(dtick=1),
        boxmode='group',
        boxgap=0.1,
        boxgroupgap=0.5,
    )
    fig.update_traces(textposition='auto')
    fig.show()


def generate_random_data(resources, programs):
    data = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 15)
    for program_name in programs:
        res = random.randint(2, 14)
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

    return pd.DataFrame(
        data,
        columns=['resource', 'program', 'skill', 'start', 'end', 'effort']
    )


def main():
    fake = Faker()
    num_resources = 15
    num_programs = 5
    resources = [fake.name() for _ in range(num_resources)]
    programs = [fake.company() for _ in range(num_programs)]
    df = generate_random_data(resources, programs)
    #gantt_chart(df, y='program')
    #gantt_chart(df, y='program', bars='resource')
    #gantt_chart(df, y='program', bars='skill')
    #gantt_chart(df, y='skill')
    #gantt_chart(df, y='skill', bars='resource')
    gantt_chart(df, y='program', bars='resource')


main()


def validate_url(**kwargs):
    uri = kwargs.get('uri')
    protocol = kwargs.get('protocol')
    stem = kwargs.get('stem')
    if protocol and stem:
        uri = ':'.join([protocol, stem])
    elif uri:
        protocol, stem = uri.split(':')
    assert stem and protocol, 'Protocol and/or Stem missing'
    protocols = DNS.enums('PROTOCOLS')
    assert protocol in protocols, f'Protocol {protocol} not in {protocols}'
    kwargs['uri'] = uri


class Repo:

    def __init__(self, uri):
        return uri


class DNS:

    @classmethod
    def enums(cls, enum, **kwargs):
        if enum == 'PROTOCOLS':
            return [
                'qzt', 'txf', 'http', 'csv', 'xls', 'pd', 'obs', 'rra', 'kudu',
                'dict', 'list'
            ]
        else:
            return kwargs

    def repo(self, **kwargs):
        validate_url(**kwargs)
        return Repo(kwargs.get('uri'))

    def pivot(self, **kwargs):
        pass

    def find(self, **kwargs):
        pass

    def first(self, **kwargs):
        pass

    def top(self, **kwargs):
        pass

    def join(self, **kwargs):
        pass

    def mailer(self, **kwargs):
        pass

    def sftp(self, **kwargs):
        pass

    def dq(self, **kwargs):
        pass

    def xform(self, from_='qzt', to='pd'):
        pass

    def xlation_map(self, **kwargs):
        pass

    def xlate(self, to='human', row=None, col=None):
        pass

    def beautify(self, **kwargs):
        pass
