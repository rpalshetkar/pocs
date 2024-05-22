import re

import pandas as pd
import sidetable


def run():
    pd.set_option("display.float_format", "{:10,.0f}".format)
    index = ["Year"]
    values = ["Value1"]
    index = ["Year", "Quarter", "Month", "Class"]
    values = ["Value1", "Value2"]
    columns = ["Category"]
    subtotals = ['Quarter']
    data = {
        "Year": ["2019", "2019", "2019", "2021", "2022", "2023"],
        "Quarter": ["Q1", "Q1", "Q2", "Q1", "Q2", "Q2"],
        "Month": ["Jan", "Feb", "Mar", "Jan", "Feb", "Mar"],
        "Class": ["A1", "A2", "B1", "A", "B", "B"],
        "Category": ["A", "A", "B", "A", "B", "B"],
        "Value1": [-10000, 20000, -30000, -15000, -25000, 35000],
        "Value2": [10000, -20000, -40000, 55000, 5000, 5000],
    }
    df = pd.DataFrame(data)
    pdf = pivot_df(
        df,
        index=index,
        columns=columns,
        values=values,
        subtotals=subtotals,
    )
    with open("pivot_table.html", "w") as f:
        htm = htmlize(pdf)
        f.write(htm)


def pivot_df(df, index, columns, values, subtotals):
    pdf = df.pivot_table(
        index=index,
        columns=columns,
        values=values,
        fill_value=0,
        aggfunc="sum",
    )
    if subtotals:
        levels = [
            i + 1 for i, v in enumerate(index + columns) if v in subtotals
        ]
        pdf = pdf.groupby(index).sum().stb.subtotal(
            sub_level=levels,
            grand_label="ALL",
            sub_label="S/T",
            show_sep=True,
            sep="-",
        )
        pdf.index.names = index
    return pdf


def htmlize(pivot_df, colors=None):

    if not colors:
        colors = {
            "bg": "white",
            "total_txt": "crimson",
            "x_value": [0, 1000, 2000],
            "x_colors": ['red', 'blue', 'green'],
        }

    def _format_values_html(x):
        print(x.index)
        arr = list(x.name) if isinstance(x.name, tuple) else [x.name]
        is_total = any(re.search("total", i.lower()) for i in arr)
        for k, v in x.items():
            x[k] = _format_value(v, is_html=True, is_total=is_total)
        return x

    def _format_value(x, is_html=False, is_total=False):
        try:
            num = f"{x:,.0f}"
            if not is_html:
                return num
            style = "font-size:14 !important;text-align: right; display:block;"
            style += "width: 100%; height: 100%;"
            style += "background-color: white;"
            style += "font-weight:bold;"
            if is_total:
                style += f'color:{"crimson" if x < 0 else "green"};'
            else:
                style += f'color:{"red" if x < 0 else "green"};'
                if abs(x) > 10000:
                    style += "background-color:yellow;"
                elif abs(x) > 20000:
                    style += "background-color:red;"
            txt = f'<span style="{style}">{num}</span>' if style else num
        except Exception as e:
            print(f"Error converting {x} ({e})")
            txt = x
        return txt

    html = pivot_df.apply(_format_values_html, axis=1)
    rep_html = html.to_html(escape=False)

    # Add styles to the HTML
    styles = """
    <style type="text/css">

    table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }

    thead tr {
        background-color: #009875;
        color: #ffffff;
        text-align: left;
        font-weight: bold;
    }

    th, td {
        padding: 12px 15px;
    }


    tbody tr {
        border-bottom: 1px solid #dddddd;
        text-align: left;
    }

    tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }

    tbody trx:last-of-type {
        border-bottom: 2px solid #009879;
    }

    tbody tr.active-row {
        font-weight: bold;
        color: #009850;
    }
    </style>
    """

    return f"{styles}\n{rep_html}"


run()
"""
def pivot_old(df, index, columns, values):
    # Create the initial pivot table
    pd.set_option("display.float_format", "{:10,.0f}".format)
    pivot_df = df.pivot_table(
        index=index,
        values=values,
        columns=columns,
        fill_value=0,
        aggfunc="sum",
    )

    subtotals = []

    def _subtotal_index(subtotal):
        sub_index = []
        for idx in subtotal.index:
            if not isinstance(idx, tuple):
                idx = (idx,)
            nidx = idx
            if len(index) - len(idx) > 0:
                x = (f"{idx[-1]}(Total)",)
                x = ("Total",)
                nidx = nidx + x
            nidx = nidx + tuple([""] * (len(index) - len(nidx)))
            sub_index.append(nidx)
        print(subtotal.index, sub_index)
        return sub_index

    for level in range(len(index)):
        subtotal = None
        if level == len(index) - 1:
            pivot_df["ALL"] = "ALL"
            subtotal = pivot_df.groupby(["ALL"]).sum()
        else:
            subtotal = pivot_df.groupby(level=index[:level + 1]).sum()
        idx = _subtotal_index(subtotal)
        subtotal.index = pd.MultiIndex.from_tuples(idx, names=index)
        subtotals.append(subtotal)

    result = pd.concat([pivot_df] + subtotals)

    def custom_sort_key(key):
        return [(2, "") if re.search("ALL", item) else
                (1, "") if re.search("Total", item) else (0, item)
                for item in key]

    sorted_index = sorted(result.index, key=custom_sort_key)
    result = result.reindex(sorted_index)
    result.drop(columns=[("ALL", "")], inplace=True)
    return result
"""
