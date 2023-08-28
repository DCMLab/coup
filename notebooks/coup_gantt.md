---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.15.0
kernelspec:
  display_name: ms3
  language: python
  name: ms3
---

```{code-cell} ipython3
%load_ext autoreload
%autoreload 2

from fractions import Fraction as frac

from ms3 import Parse
from ms3.utils import transform, roman_numeral2fifths, roman_numeral2semitones, name2fifths, rel2abs_key, labels2global_tonic, resolve_relative_keys
from plotly.offline import plot #init_notebook_mode, iplot
#import plotly.graph_objs as go
import plotly.figure_factory as ff
import pandas as pd
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
```

```{code-cell} ipython3
folder = '~/couperin_concerts/harmonies'
p = Parse(folder, file_re='tsv$')
p.parse_tsv()
p
```

```{code-cell} ipython3
md = pd.read_csv('~/couperin_concerts/metadata.tsv', sep='\t', index_col=1)
md.head()
```

```{code-cell} ipython3
def create_gantt(d, task_column='Task', title='Gantt chart', lines=None, cadences=None):
    """Creates and returns ``fig`` and populates it with features.

    When plotted with plot() or iplot(), ``fig`` shows a Gantt chart representing
    the piece's tonalities as extracted by the class Keys().

    Parameters
    ----------
    d: pd.Dataframe
        DataFrame with at least the columns ['Start', 'Finish', 'Task', 'Resource'].
        Other columns can be selected as 'Task' by passing ``task_column``. 
        Further possible columns: 'Description'
    task_column : str
        If ``d`` doesn't have a 'Task' column, pass the name of the column that you want to use as such.
    title: str
        Title to be plotted

    Examples
    --------

    >>> iplot(create_gantt(df))

    does the same as

    >>> fig = create_gantt(df)
    >>> iplot(fig)

    To save the chart to a file instead of displaying it directly, use

    >>> plot(fig,filename="filename.html")
    """

    colors = {'applied': 'rgb(228,26,28)', # 'rgb(220, 0, 0)',
              'local': 'rgb(55,126,184)',  # (1, 0.9, 0.16),
              'tonic of adjacent applied chord(s)': 'rgb(77,175,74)'} # 'rgb(0, 255, 100)'}
    # 'Bluered', 'Picnic', 'Viridis', 'Rainbow'
    
    if task_column != 'Task':
        d = d.rename(columns={task_column: 'Task'})


    fig = ff.create_gantt(d,colors=colors,group_tasks=True,index_col='Resource',show_colorbar=True,
                       showgrid_x=True, showgrid_y=True ,title=title)

    fig['layout']['xaxis'].update({'type': None, 'title': 'Measures'})
    fig['layout']['yaxis'].update({'title': 'Tonicized keys'})
    
    if lines is not None:
        linestyle = {'color':'rgb(0, 0, 0)','width': 0.2,'dash': 'longdash'}
        lines = [{'type': 'line','x0':position,'y0':0,'x1':position,'y1':20,'line':linestyle} for position in lines]
        fig['layout']['shapes'] = fig['layout']['shapes'] + tuple(lines)
        
            

    if cadences is not None:
        lines = []
        annos = []
        hover_x = []
        hover_y = []
        hover_text = []
        alt = 0
        for i,r in cadences.iterrows():
            m = r.m
            c = r.type
            try:
                key = r.key
            except:
                key = None

            if c == 'PAC':
                c = 'PC'
                w = 1
                d = 'solid'
            elif c == 'IAC':
                c = 'IC'
                w = 0.5
                d = 'solid'
            elif c == 'HC':
                w = 0.5
                d = 'dash'
            elif c == 'EVCAD':
                c = 'EC'
                w = 0.5
                d = 'dashdot'
            elif c == 'DEC':
                c = 'DC'
                w = 0.5
                d = 'dot'
            else:
                print(f"{c}: Kadenztyp nicht vorgesehen")
            #c = c + f"<br>{key}"
            linestyle = {'color':'rgb(55, 128, 191)','width': w,'dash':d}
            annos.append({'x':m,'y':-0.01+alt*0.03,'font':{'size':7},'showarrow':False,'text':c,'xref':'x','yref':'paper'})
            lines.append({'type': 'line','x0':m,'y0':0,'x1':m,'y1':20,'line':linestyle})
            alt = 0 if alt else 1
            hover_x.append(m)
            hover_y.append(-0.5 - alt * 0.5)
            text = "Cad: " + r.type
            if key is not None:
                text += "<br>Key: " + key
            text += "<br>Beat: " + str(r.beat)
            hover_text.append(text)



        fig['layout']['shapes'] = fig['layout']['shapes'] + tuple(lines)
        fig['layout']['annotations'] = annos

        hover_trace=dict(type='scatter',opacity=0,
                        x=hover_x,
                        y=hover_y,
                        marker= dict(size= 14,
                                    line= dict(width=1),
                                    color= 'red',
                                    opacity= 0.3),
                        name= "Cadences",
                        text= hover_text)
        #fig['data'].append(hover_trace)
        fig.add_traces([hover_trace])
    return fig
```

```{code-cell} ipython3
#create_gantt(make_gantt_data(at), task_column='semitones', lines=phrases)
```

```{code-cell} ipython3
def make_gantt_data(at, last_mn=None, relativeroots=True):
    """ Uses: rel2abs_key, resolve_relative_keys, roman_numeral2fifths roman_numerals2semitones, labels2global_tonic
    """
    at = at[at.numeral.notna() & (at.numeral != '@none')].copy()
    if 'mn_fraction' not in at.columns:
        mn_fraction = (at.mn + (at.mn_onset.astype(float)/at.timesig.map(frac).astype(float))).astype(float)
        at.insert(at.columns.get_loc('mn')+1, 'mn_fraction', mn_fraction)
    if last_mn is None:
        last_mn = at.mn.max()
    at.sort_values('mn_fraction', inplace=True)
    interval_breaks = at.mn_fraction.append(pd.Series(last_mn+1.0), ignore_index=True)
    at.index = pd.IntervalIndex.from_breaks(interval_breaks, closed='left')
    
    key_groups = at.loc[at.localkey != at.localkey.shift(), ['mn_fraction', 'localkey', 'globalkey', 'globalkey_is_minor']].rename(columns={'mn_fraction': 'Start'})
    key_groups['numeral'] = key_groups.localkey
    key_groups.insert(2, 'semitones', transform(key_groups, roman_numeral2semitones, ['numeral', 'globalkey_is_minor']))
    key_groups.insert(2, 'fifths', transform(key_groups, roman_numeral2fifths, ['numeral', 'globalkey_is_minor']))
    interval_breaks = key_groups.Start.append(pd.Series(last_mn+1.0), ignore_index=True)
    iix = pd.IntervalIndex.from_breaks(interval_breaks, closed='left')
    key_groups.index = iix
    insert_pos = key_groups.columns.get_loc('Start')+1
    key_groups.insert(insert_pos, 'Resource', 'local')
    key_groups.insert(insert_pos, 'Duration', iix.length)
    key_groups.insert(insert_pos, 'Finish', iix.right)
    
    if not relativeroots or at.relativeroot.isna().all():
        return key_groups
    
    levels = list(range(at.index.nlevels))
    def select_groups(df):
        nonlocal levels
        has_applied = df.Resource.notna()
        if has_applied.any():
            df.Resource.fillna('tonic of adjacent applied chord(s)', inplace=True)
            df.relativeroot = df.relativeroot.where(has_applied, df.numeral)
            df['subgroup'] = df.Resource != df.Resource.shift()
            return df
        else:
            return pd.DataFrame(columns=levels).set_index(levels, drop=True)
        
    def gantt_data(df):
        frst = df.iloc[[0]]
        start, finish = df.index[0].left, df.index[-1].right
        frst['Start'] = start
        frst['Finish'] = finish
        frst['Duration'] = finish - start
        frst.index = pd.IntervalIndex.from_tuples([(start, finish)], closed='left')
        return frst
    
    key_groups['abs_numeral'] = key_groups.localkey
    global_numerals = labels2global_tonic(at).numeral
    at['Resource'] = pd.NA
    at.Resource = at.Resource.where(at.relativeroot.isna(), 'applied')
    at['relativeroot_resolved'] = transform(at, resolve_relative_keys, ['relativeroot', 'localkey_is_minor'])
    at['abs_numeral'] = transform(at, rel2abs_key, ['relativeroot_resolved', 'localkey', 'globalkey_is_minor'])
    at.abs_numeral = at.abs_numeral.where(at.abs_numeral.notna(), global_numerals)
    #print(global_numerals)
    #print(at.abs_numeral)
    at['fifths'] = transform(at, roman_numeral2fifths, ['abs_numeral', 'globalkey_is_minor'])
    at['semitones'] = transform(at, roman_numeral2semitones, ['abs_numeral', 'globalkey_is_minor'])
    # using the semitones column includes adjacent variant labels;
    # if only labels of the same mode are to be included, use the numeral column
    adjacent_groups = (at.semitones != at.semitones.shift()).cumsum()
    try:
        at = at.groupby(adjacent_groups, group_keys=False).apply(select_groups).astype({'semitones': int, 'fifths': int})
    except:
        print(at.groupby(adjacent_groups, group_keys=False).apply(select_groups))
        raise
    at.subgroup = at.subgroup.cumsum()
    at = at.groupby(['subgroup', 'localkey'], group_keys=False).apply(gantt_data)
    res = pd.concat([key_groups, at])[['Start', 'Finish', 'Duration', 'Resource', 'abs_numeral', 'fifths', 'semitones', 'localkey', 'globalkey', 'relativeroot']]
    res[['Start', 'Finish', 'Duration']] = res[['Start', 'Finish', 'Duration']].round(2)
    res['Description'] = 'Duration: ' + res.Duration.astype(str) + '<br>Tonicized key: ' + res.abs_numeral + ('<br>In context of localkey ' + res.localkey + ': ' + res.relativeroot).fillna('')
    return res

def get_phraseends(at):
    if 'mn_fraction' not in at.columns:
        mn_fraction = at.mn + (at.mn_onset.astype(float)/at.timesig.map(frac).astype(float))
        at.insert(at.columns.get_loc('mn')+1, 'mn_fraction', mn_fraction)
    return at.loc[at.phraseend.notna(), 'mn_fraction'].to_list()
```

```{code-cell} ipython3
i = 7
fname = p.fnames['.'][i]
metadata = md.loc[fname]
last_mn = metadata.last_mn
globalkey = metadata.annotated_key
at = p._parsed_tsv[('.', i)]
make_gantt_data(at, last_mn=last_mn, relativeroots=True)
#labels2global_tonic(at, inplace=True)
```

```{code-cell} ipython3
p.parsed_tsv.head()
```

```{code-cell} ipython3
p._parsed_tsv.keys()
```

```{code-cell} ipython3
USE = 'semitones' # choose from 'semitones', 'fifths', 'numeral'
for i, fname in enumerate(p.fnames['.']):
    print(i, fname)
    metadata = md.loc[fname]
    last_mn = metadata.last_mn
    globalkey = metadata.annotated_key
    at = p._parsed_tsv[('.', i)]
    data = make_gantt_data(at, last_mn=last_mn, relativeroots=True)
    phrases = get_phraseends(at)
    data.sort_values(USE, ascending=False, inplace=True)
    fig = create_gantt(data, title=f"{fname} ({globalkey})", task_column=USE, lines=phrases)
    plot(fig, filename=f'docs/coup_gantt/{fname}.html')
```

```{code-cell} ipython3
for f in sorted(p.fnames['.']):
    print(f'<iframe id="igraph" scrolling="no" style="border:none;" seamless="seamless" src="coup_gantt/{f}.html" height="600" width="100%"></iframe>')
```

```{code-cell} ipython3

```
