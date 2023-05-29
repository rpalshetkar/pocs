import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs

def read_apls(products, apl_csv):
    df = pd.read_csv(apl_csv)
    df = df.assign(Product=df['Products'].str.split(',')) \
        .explode('Product').reset_index(drop=True)
    df['Currencies'].fillna('ALL', inplace=True)
    df = df.assign(Currency=df['Currencies'].str.split(',')) \
        .explode('Currency').reset_index(drop=True)
    df.reset_index()
    df = df.fillna('')
    df = df[['Entity', 'Asset Class', 'Product', 'Currency']]
    if df['Product'].empty:
        new_df = pd.concat([df] *len(products.keys()))
        new_df['Product'] = [item for sublist in products.values() for item in sublist]
        df = pd.concat([df, new_df])
    df['Currency'].fillna('ALL', inplace=True)
    print(df)
    return df


def read_infra(infra_csv):
    df = pd.read_csv(infra_csv)
    df = df.fillna('')
    return df


def read_capabilities():
    capabilities = [
        'Trading/TR0/Marking',
        'Trading/TR1/Pricing',
        'Trading/TR2/Electronic Trading',
        'Trading/TR3/Trading Venue',
        'Trading/TR4/Trade Management',
        'Trading/TR5/Trading Risk',
        'Trading/TR6/Auctions',
        'Trading/TR7/Trade Submissions',
        'Trading/TR8/Flash Risk',
        'Trading/TR9/Intraday Risk Monitoring',
        'Operations/OP1/Documentation',
        'Operations/OP2/Corporate Actions',
        'Operations/OP3/Settlements',
        'Enterprise/TR10/Marking',
        'Enterprise/TR11/Flash PL',
        'Enterprise/TR12/Flash Risk',
        'Enterprise/TR13/EOD Official',
        'Enterprise/FN1/Finance SubGL',
        'Enterprise/FN1/Finance GL',
        'Enterprise/ER1/Market Risk',
        'Enterprise/ER2/Credit Risk',
        'Enterprise/RG1/Regulatory Reporting',
    ]
    capabilities = [i.split('/') for i in capabilities]
    return pd.DataFrame([list(reversed(i)) for i in capabilities],
                        columns=['Capability', 'Order', 'Function'])


def find_matches(apls, infras, capabilities):
    matches = []
    apls = apls.to_dict('records')
    infras = infras.to_dict('records')
    capabilities = capabilities.to_dict('records')
    for apl in apls:
        for c in capabilities:
            capability = c['Capability']
            finfras = [i for i in infras if i['Capability'] == capability]
            which= []
            for infra in finfras:
                score = 0
                if infra['Entity'] in [apl['Entity'], 'Asia'] and \
                   infra['Asset Class'] in [apl['Asset Class'], ''] and \
                   infra['Product'] in [apl['Product'], '']:
                    score += 2
                if score > 0:
                    ref = infra | apl
                    ref['Score'] = score
                    which.append(ref)
            if which:
                which.sort(key=lambda x: x['Score'])
                matches.append(which[-1])
    df = pd.DataFrame(matches)
    pd.set_option('display.max_rows', 1500)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', 200)
    pd.set_option('expand_frame_repr', True)
    pd.set_option('display.width', 20000)
    pd.set_option('display.float_format', '{:10,.0f}'.format)
    #flds = ['Entity', 'Asset Class', 'Product', 'Capability']
    #df.sort_values('Score', ascending=False).drop_duplicates(subset=flds)
    df = df[['Entity', 'Capability', 'Asset Class',
             'Product', 'Currency', 'System',
             'Measure', 'Value', 'Score']]
    #df = df.sort_values(['Entity','Capability'], ascending=False)
    #df['Value'] = np.random.randint(10, 101, size=len(df))
    print(df)
    return df

def heatmap(hdf, row, col):
    colors = [
        'viridis',
        'plasma',
        'inferno',
        'magma',
        'cividis',
        'coolwarm',
        'YlGnBu',
        'PuBu',
        'BuPu',
        'Greys',
        'Purples',
        'Blues',
        'Greens',
        'Oranges',
        'Reds',
    ]
    cols = [row, col]
    df = hdf.copy();
    if 'Product' in cols:
        df['Product'] = df['Asset Class'] + '/' + df['Product']
    df = df.groupby(cols)['Value'].mean().reset_index()
    #df['Value']=(df['Value']-df['Value'].min() + 0.01)*100./ \
        #(df['Value'].max()-df['Value'].min())
    df = df.astype({'Value':'int'})
    pivot = df.pivot(index=[row], columns=col, values='Value')
    color = colors[6]
    color = sns.color_palette("RdYlGn", as_cmap=True)

    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.xlabel(col, fontsize=10)
    plt.ylabel(row, fontsize=10)
    plt.title(f'Heatmap {row}/{col}', fontsize=12)
    annot = False
    sns.heatmap(data=pivot, cmap=color, square=True, 
                linewidths=1, linecolor='gray', annot=annot, fmt='g')
    #plt.subplots_adjust(left=0.3, right=0.9, bottom=0.3)
    plt.tight_layout()
    plt.show()



def main():
    products = {
        'FX': ['Spots', 'Forwards', 'NDFs', 'Swaps', 'Options', 'TFX', 'CFXO'],
        'Bonds': ['Govt'],
        'FNO': ['Bonds', 'ED', 'FX', 'EFPs'],
        'Rates': ['IRS', 'CCS', 'NDIRS', 'TRS', 'BFWD','VIRO','CIRO'],
        'Repos': ['TERM', 'SHORT'],
        'Treasury': ['Loans', 'Deposits']
    }
    apls=read_apls(products, 'apls.csv')
    infra=read_infra('infra.csv')
    capabilities=read_capabilities()
    hdf = find_matches(apls, infra, capabilities)
    #heatmap(hdf, 'Entity', 'Capability')
    #heatmap(hdf, 'Asset Class', 'Capability')
    #heatmap(hdf, 'Capability', 'System')
    heatmap(hdf, 'Capability', 'System')
    heatmap(hdf, 'Entity', 'Capability')
    heatmap(hdf, 'Entity', 'Product')
    heatmap(hdf, 'Capability', 'Product')

main()
