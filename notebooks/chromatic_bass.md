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
from ms3 import Parse
from ms3.utils import transform, roman_numeral2tpc, fifths2pc, fifths2name, name2tpc
import pandas as pd
pd.options.display.max_columns = 50
pd.options.display.max_rows = 100
```

# Load expanded ABC labels

```{code-cell} ipython3
dir = '/home/hentsche/ABC/harmonies'
p = Parse(dir, key='abc', file_re='tsv$', index='fname')
p.parse_tsv()
p
```

```{code-cell} ipython3
labels = p.get_labels().sort_index().iloc[:,:-3]
labels
```

# Transform `bass_note` column

+++

## Expressing all bass notes as scale scale degrees of global tonic
Since all scale degrees are expressed as fifths-intervals, this is as easy as adding the local key expressed as fifths

```{code-cell} ipython3
transpose_by = transform(labels, roman_numeral2tpc, ['localkey', 'globalkey_is_minor'])
bass = labels.bass_note + transpose_by
bass.head()
```

## Adding bass note names to DataFrame

```{code-cell} ipython3
transpose_by = transform(labels, name2tpc, ['globalkey'])
labels['bass_name'] = fifths2name(bass + transpose_by).values
labels.head()
```

## Calculating intervals between successive bass notes
Sloppy version: Include intervals across movement boundaries

### Bass progressions expressed in fifths

```{code-cell} ipython3
bass = bass.bfill()
ivs = bass - bass.shift()
ivs.value_counts()
```

### Bass progressions expressed in (enharmonic) semitones

```{code-cell} ipython3
pc_ivs = fifths2pc(ivs)
pc_ivs.index = ivs.index
pc_ivs = pc_ivs.where(pc_ivs <= 6, pc_ivs % -6).fillna(0)
pc_ivs.value_counts()
```

# Chromatic bass progressions

```{code-cell} ipython3
def cnt(S, interval, k_min=1, df=True):
    ix_chunks = pd.DataFrame(columns=['ixs', 'n']) if df else []
    current = []
    n = 0
    for i, iv in S.iteritems():
        
        if iv in [0, interval]:
            current.append(i)
            if iv == interval:
                n += 1
        else:
            if n >= k_min:
                if df:
                    ix_chunks = ix_chunks.append(pd.Series((current, n), index=['ixs', 'n']), ignore_index=True)
                else:
                    ix_chunks.append((current, n))
            current = [i]
            n = 0
    return ix_chunks
```

## Successive descending semitones

```{code-cell} ipython3
desc = cnt(pc_ivs, -1)
desc.n.value_counts()
```

### Storing those with three or more

```{code-cell} ipython3
three_desc = labels.loc[desc[desc.n > 2].ixs.sum()]
three_desc.to_csv('three_desc.tsv', sep='\t')
three_desc.head(30)
```

### Storing those with four or more

```{code-cell} ipython3
four_desc = labels.loc[desc[desc.n > 3].ixs.sum()]
four_desc.to_csv('four_desc.tsv', sep='\t')
four_desc.head(30)
```

## Successive ascending semitones

```{code-cell} ipython3
asc = cnt(pc_ivs, 1)
asc.n.value_counts()
```

### Storing those with three or more

```{code-cell} ipython3
three_asc = labels.loc[asc[asc.n > 2].ixs.sum()]
three_asc.to_csv('three_asc.tsv', sep='\t')
three_asc.head(30)
```

### Storing those with four or more

```{code-cell} ipython3
four_asc = labels.loc[asc[asc.n > 3].ixs.sum()]
four_asc.to_csv('four_asc.tsv', sep='\t')
four_asc.head(30)
```

# Filtering for particular progressions with length >= 3
Finding only direct successors

```{code-cell} ipython3
def filtr(df, query, column='chord'):
    vals = df[column].to_list()
    n_grams = [t for t in zip(*(vals[i:] for i in range(len(query))))]
    if isinstance(query[0], str):
        lengths = [len(q) for q in query]
        n_grams = [tuple(e[:l] for e,l  in zip(t, lengths)) for t in n_grams]
    return query in n_grams

def show(df, query, column='chord'):
    selector = df.groupby(level=0).apply(filtr, query, column)
    return df[selector[df.index.get_level_values(0)].values]
```

## Descending

```{code-cell} ipython3
descending = pd.concat([labels.loc[ix_seq] for ix_seq in desc[desc.n > 2].ixs.values], keys=range((desc.n > 2).sum()))
descending
```

### Looking for `Ger i64`

```{code-cell} ipython3
show(descending, ('Ger', 'i64'))
```

### `i64`

```{code-cell} ipython3
show(descending, ('i64',))
```

### `Ger V(64)`

```{code-cell} ipython3
show(descending, ('Ger', 'V(64'))
```

### Bass degrees `b6 5 #4`

```{code-cell} ipython3
show(descending, (-4, 1, 6), 'bass_note')
```

## Ascending

```{code-cell} ipython3
ascending = pd.concat([labels.loc[ix_seq] for ix_seq in asc[asc.n > 2].ixs.values], keys=range((asc.n > 2).sum()))
ascending = ascending[ascending.label != '@none']
ascending
```

### `i64 Ger`

```{code-cell} ipython3
show(ascending, ('i64', 'Ger'))
```

### `i64`

```{code-cell} ipython3
show(ascending, ('i64',))
```

### `V(64) Ger`

```{code-cell} ipython3
show(ascending, ('V(64)', 'Ger'))
```

### Bass degrees `#4 5 b6`

```{code-cell} ipython3
show(ascending, (6, 1, -4), 'bass_note')
```
