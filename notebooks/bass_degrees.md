---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.15.1
kernelspec:
  display_name: coup
  language: python
  name: coup
---

# Bass degrees

```{code-cell} ipython3
%load_ext autoreload
%autoreload 2
# pip install ms3 pandas plotly seaborn scipy
import os
os.chdir("/home/laser/git/coup/notebooks")
from collections import Counter, defaultdict
import ms3
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from helpers import cnt, transition_matrix, plot_bigram_tables, prettify_counts, sorted_gram_counts
import dimcat as dc

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
```

```{code-cell} ipython3
CORPUS_PATH = '~/all_subcorpora/couperin_concerts'
RESULTS_PATH = os.path.abspath(os.path.join("..", "results"))
```

**Loading data**

```{code-cell} ipython3
package_path = "/home/laser/all_subcorpora/couperin_concerts/couperin_concerts.datapackage.json"
D = dc.Dataset.from_package(package_path)
D
```

**All labels**

```{code-cell} ipython3
labels = D.get_feature('harmonylabels')
df = labels.df.droplevel(0)
df.head(20)
```

## Bass degree unigrams
As expressed by the annotation labels.

```{code-cell} ipython3
bd = df.bass_note.value_counts()
print(f"N = {len(df)}")
fig = px.bar(x=ms3.fifths2sd(bd.index.to_list()), y=bd.values, 
             labels=dict(x='Scale degree in relation to major scale', y='count'),
             title="Distribution of all bass degrees",
             color_discrete_sequence =['grey']*len(bd))
fig.update_xaxes(type='category')
fig.show()
```

```{code-cell} ipython3
localkey_is_major = ~df.localkey_is_minor
print(f"N = {localkey_is_major.sum()}")
bd_maj = df[localkey_is_major].bass_note.value_counts()
fig = px.bar(bd_maj, x=ms3.fifths2sd(bd_maj.index.to_list(), minor=False), y=bd_maj.values, 
             labels=dict(x='Scale degree in relation to major scale', y='count'), 
             title="Distribution of bass degrees in major segments",
             color_discrete_sequence =['blue']*len(bd_maj))
fig.update_xaxes(type='category')
fig.show()
```

```{code-cell} ipython3
print(f"N = {df.localkey_is_minor.sum()}")
bd_min = df[df.localkey_is_minor].bass_note.value_counts()
fig = px.bar(bd_min, x=ms3.fifths2sd(bd_min.index.to_list(), minor=True), y=bd_min.values, 
             labels=dict(x='Scale degree in relation to minor scale', y='count'), 
             title="Distribution of bass degrees in minor segments",
             color_discrete_sequence =['red']*len(bd_min))
fig.update_xaxes(type='category')
fig.show()
```

**Note: When dropping immediate repetitions of the same bass degree (see transition matrices below), minor segments, too, have 1 as the most frequent bass degree. This can be linked to frequent suspensions over bass degree 5.**

+++

## Intervals between adjacent bass notes
### Preparing the data
#### Get localkey segments

```{code-cell} ipython3
df['key_regions'] = df.groupby(level=0, group_keys=False).localkey.apply(lambda col: col != col.shift()).cumsum()
df['bass_degree'] = ms3.transform(df, ms3.fifths2sd, ['bass_note', 'localkey_is_minor'])
```

```{code-cell} ipython3
segment_lengths = df.groupby('key_regions').size()
segment_lengths_aggr = segment_lengths.value_counts()
px.bar(x=segment_lengths_aggr.index, y=segment_lengths_aggr, labels=dict(x='#labels', y='number of key segments with particular length'))
```

```{code-cell} ipython3
# Show all segments of length L
L = 1
selected = segment_lengths[segment_lengths == L].index
df[df.key_regions.isin(selected)]
```

#### Delete @none labels
This creates progressions between the label before and after the `@none` label that might not actually be perceived as transitions!

```{code-cell} ipython3
print(f"Length before: {len(df.index)}")
is_none = (df.chord == '@none').fillna(False)
print(f"There are {is_none.sum()} @none labels which we are going to delete.")
df.drop(df.index[is_none], inplace=True)
print(f"Length after: {len(df.index)}")
```

#### Delete non-chord labels (typically, phrase labels)

```{code-cell} ipython3
print(f"Length before: {len(df.index)}")
non_chord = df.chord.isna()
print(f"There are {non_chord.sum()} non-chord labels which we are going to delete:")
display(df.loc[non_chord, "label"].value_counts())
df.drop(df.index[non_chord], inplace=True)
print(f"Length after: {len(df.index)}")
```

### Get bass degree progressions & intervals
All scale degrees are expressed as fifth-intervals to the local tonic:

| fifths-interval | interval    |
|-----------------|-------------|
| -3              | m3          |
| -2              | m7          |
| -1              | P4          |
| 0               | local tonic |
| 1               | P5          |
| 2               | M2          |
| 3               | M6          |

```{code-cell} ipython3
bd_series = {seg: bn for seg, bn in  df.groupby('key_regions').bass_note}
bd_intervals = {seg: bd - bd.shift() for seg, bd in bd_series.items()}
df['bass_interval'] = df.groupby('key_regions', group_keys=False).bass_note.apply(lambda bd: bd - bd.shift())
print("Example output for the intervals of the first key segment:")
df.loc[df.key_regions==1, ['bass_note', 'bass_interval']]
```

#### Count bass intervals

```{code-cell} ipython3
interval_counter = Counter()
for S in bd_intervals.values():
    interval_counter.update(S.dropna())
interval_counter
```

```{code-cell} ipython3
bar_data = pd.Series(interval_counter).sort_values(ascending=False)
fig = px.bar(x=ms3.fifths2iv(bar_data.index.to_list()), y=bar_data.values, 
             labels=dict(x='Interval between adjacent bass notes', y='count'),
             title="Distribution of all bass intervals (within the same localkey)",
             color_discrete_sequence =['grey']*len(bd))
fig.update_xaxes(type='category')
fig.show()
```

**

```{code-cell} ipython3
px.bar(x=interval_counter.keys(), y=interval_counter.values(), labels=dict(x='interval in fifths', y='count'), title='Orderd on the line of fifths')
```

```{code-cell} ipython3
iv_order = [-6, 1, 8, -11, -4, 3, 10, -9, -2, 5, 12, -7, 0, 7, -5, 2, 9, -10, -3, 4, 11, -8, -1, 6] # do not occur: -11, -10, 11
iv_counter = {ms3.fifths2iv(i, True): interval_counter[i] for i in iv_order if i in interval_counter}
px.bar(x=iv_counter.keys(), y=iv_counter.values(), labels=dict(x='interval', y='count'), title='Ordered by base '
                                                                                               'interval')
```

```{code-cell} ipython3
iv_order = [12, 10, -9, -6, -7, 8, -4, 5, 1, 3, -2, 0, -1, 2, -5, 4, -3, 6, 7, -8, 9] # do not occur: -11, -10, 11
iv_counter = {ms3.fifths2iv(i): interval_counter[i] for i in iv_order if i in interval_counter}
px.bar(x=iv_counter.keys(), y=iv_counter.values(), labels=dict(x='interval', y='count'), title='Ordered around the unison')
```

```{code-cell} ipython3
px.bar(x=sorted(iv_counter.keys(), key=lambda k: iv_counter[k], reverse=True), y=sorted(iv_counter.values(), reverse=True), labels=dict(x='interval', y='count'), title='Descending frequency')
```

### Checking rare intervals

**occurrences of -9 (-A2)**

* `c02n01_prelude` m. 12: `ii%` was corrected to `iii%`

The other two were correct: 

* `c07n05_gavote` m. 27: progression `V65 VIM7` in minor
* `c03n05_gavotte` m. 22: progression `V65 ii%43` (in minor)

```{code-cell} ipython3
# see all key regions containing a certain interval in the bass
bass_interval = -9
selected = df.loc[df.bass_interval==bass_interval].key_regions.unique()
df.loc[df.key_regions.isin(selected), ["mc", "mn", "chord", "bass_degree", "bass_interval"]]
```

### Inspecting stepwise bass movement

**Add column with bass interval in semitones.**
It's called `bass_interval_pc` as in "pitch class"

```{code-cell} ipython3
pc_ivs = ms3.transform(df, ms3.fifths2pc, ['bass_interval'])
df['bass_interval_pc'] = pc_ivs.where(pc_ivs <= 6, pc_ivs % -6)
```

```{code-cell} ipython3
df[["mc", "mn", "bass_degree", "bass_interval", "bass_interval_pc"]].head(15)
```

#### Create key region summary

**With one row per key region and the following columns**

| **column**            | what it contains                                               |
|-----------------------|----------------------------------------------------------------|
| **globalkey**         | the global key of the segment                                  |
| **localkey**          | the local key of the segment                                   |
| **length**            | number of labels                                               |
| **length_norepeat**   | number of labels without immediate repetitions                 |
| **n_stepwise**        | number of stepwise bass progressions                           |
| **%_stepwise**        | percentage of stepwise progressions (based on length_norepeat) |
| **n_ascending**       | number of stepwise ascending bass progressions                 |
| **n_descending**      | number of stepwise descending bass progressions                |
| **bd**                | full sequence of bass degrees                                  |
| **stepwise_bd**       | all sequences of consecutive stepwise bass progressions        |
| **stepwise_chords**   | the corresponding chord sequences                              |
| **ascending_bd**      | the subset of ascending bass progressions                      |
| **ascending_chords**  | the corresponding chord sequences                              |
| **descending_bd**     | the subset of descending bass progressions                     |
| **descending_chords** | the corresponding chord sequences                              |
| **ixa**               | index of the segment's first row                               |
| **ixb**               | index of the segment's last row                                |

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---
def ix_segments2values(df, ix_segments, cols=['bass_degree', 'chord']):
    res = {col: [] for col in cols}
    for segment in ix_segments:
        col2list = get_cols(df, segment, cols)
        for col in cols:
            res[col].append(col2list[col])
    for col, list_of_lists in res.items():
        res[col] = [' '.join(val) for val in list_of_lists]
    return res
        

def get_cols(df, ix, cols):
    if isinstance(cols, str):
        cols = [cols]
    df = df.loc[ix]
    return {col: df[col].to_list() for col in cols}


def summarize(df):
    norepeat = (df.bass_note != df.bass_note.shift()).fillna(True)
    seconds_asc = cnt(df.bass_interval_pc, [1, 2])
    seconds_asc_vals = ix_segments2values(df, seconds_asc.ixs)
    seconds_desc = cnt(df.bass_interval_pc, [-1, -2])
    seconds_desc_vals = ix_segments2values(df, seconds_desc.ixs)
    both = cnt(df.bass_interval_pc, [1, 2, -1, -2])
    both_vals = ix_segments2values(df, both.ixs)
    n_stepwise = both.n.sum()
    length_norepeat = norepeat.sum()
    res = pd.Series({
        'globalkey': df.globalkey.unique()[0],
        'localkey': df.localkey.unique()[0],
        'length': len(df),
        'length_norepeat': length_norepeat,
        'n_stepwise': n_stepwise,
        '%_stepwise': round(100*n_stepwise/length_norepeat, 1),
        'n_ascending': seconds_asc.n.sum(),
        'n_descending': seconds_desc.n.sum(),
        'bd': ' '.join(df.loc[norepeat, 'bass_degree'].to_list()),
        'stepwise_bd': both_vals['bass_degree'],
        'stepwise_chords': both_vals['chord'],
        'ascending_bd': seconds_asc_vals['bass_degree'], #ix_segments2list(df, seconds_asc.ixs),
        'ascending_chords': seconds_asc_vals['chord'],
        'descending_bd': seconds_desc_vals['bass_degree'],
        'descending_chords': seconds_desc_vals['chord'],
        'ixa': df.index[0],
        'ixb': df.index[-1]
    })
    return res

key_regions = df.groupby('key_regions').apply(summarize)
key_regions.head(10)
```

**Store to file [key_regions.tsv](https://github.com/DCMLab/coup/blob/main/results/key_regions.tsv) for easier inspection.**

```{code-cell} ipython3
key_regions.to_csv(os.path.join(RESULTS_PATH, 'key_regions.tsv'), sep='\t')
```

```{code-cell} ipython3
print(f"{key_regions.n_stepwise.sum() / key_regions.length_norepeat.sum():.1%} of all bass movements are stepwise.")
```

```{code-cell} ipython3
def remove_immediate_repetitions(s):
    res = []
    last = ''
    for word in s.split():
        if word != last:
            res.append(word)
        last = word
    return ' '.join(res)
```

```{code-cell} ipython3
minor_selector = key_regions.localkey.str.islower()
```

```{code-cell} ipython3
minor_regions = key_regions[minor_selector]
major_regions = key_regions[~minor_selector]
```

#### All stepwise ascending bass progressions in minor

```{code-cell} ipython3
ascending_minor = defaultdict(list)
for bd, chord in zip(minor_regions.ascending_bd.sum(), minor_regions.ascending_chords.sum()):
    ascending_minor[remove_immediate_repetitions(bd)].append(chord)
ascending_minor_counts = Counter({k: len(v) for k, v in ascending_minor.items()})
prettify_counts(ascending_minor_counts)
```

```{code-cell} ipython3
show_progression = '3 4 5'
chords_3_4_5 = Counter(ascending_minor[show_progression])
prettify_counts(chords_3_4_5)
```

#### All stepwise ascending bass progressions in major

```{code-cell} ipython3
ascending_major = defaultdict(list)
for bd, chord in zip(major_regions.ascending_bd.sum(), major_regions.ascending_chords.sum()):
    ascending_major[remove_immediate_repetitions(bd)].append(chord)
ascending_major_counts = Counter({k: len(v) for k, v in ascending_major.items()})
prettify_counts(ascending_major_counts)
```

```{code-cell} ipython3
show_progression = '6 7 1'
chords_6_7_1 = Counter(ascending_major[show_progression])
prettify_counts(chords_6_7_1)
```

#### All stepwise descending bass progressions in minor

```{code-cell} ipython3
descending_minor = defaultdict(list)
for bd, chord in zip(minor_regions.descending_bd.sum(), minor_regions.descending_chords.sum()):
    descending_minor[remove_immediate_repetitions(bd)].append(chord)
descending_minor_counts = Counter({k: len(v) for k, v in descending_minor.items()})
prettify_counts(descending_minor_counts)
```

```{code-cell} ipython3
show_progression = '3 2 1'
chords_3_2_1 = Counter(descending_minor[show_progression])
prettify_counts(chords_3_2_1)
```

#### All stepwise descending bass progressions in major

```{code-cell} ipython3
descending_major = defaultdict(list)
for bd, chord in zip(major_regions.descending_bd.sum(), major_regions.descending_chords.sum()):
    descending_major[remove_immediate_repetitions(bd)].append(chord)
descending_major_counts = Counter({k: len(v) for k, v in descending_major.items()})
prettify_counts(descending_major_counts)
```

```{code-cell} ipython3
show_progression = '5 4 3'
chords_5_4_3 = Counter(descending_major[show_progression])
prettify_counts(chords_5_4_3)
```

### Transitions between bass degrees

```{code-cell} ipython3
full_grams = {i: S[( S!=S.shift() ).fillna(True)].to_list() for i, S in bd_series.items()}
print(bd_series[1])
full_grams[1]
```

```{code-cell} ipython3
minor_region_selector = key_regions.localkey.str.islower()
minor_regions = key_regions[minor_region_selector].localkey.to_dict()
major_regions = key_regions[~minor_region_selector].localkey.to_dict()
```

```{code-cell} ipython3
full_grams_minor = [ms3.fifths2sd(full_grams[i], True) + ['∅'] for i in minor_regions]
full_grams_major = [ms3.fifths2sd(full_grams[i], False) + ['∅'] for i in major_regions]
minor_unigrams = pd.Series(Counter(sum(full_grams_minor, []))).sort_values(ascending=False)
minor_unigrams_norm = minor_unigrams / minor_unigrams.sum()
major_unigrams = pd.Series(Counter(sum(full_grams_major, []))).sort_values(ascending=False)
major_unigrams_norm = major_unigrams / major_unigrams.sum()
```

```{code-cell} ipython3
minor_bigrams = transition_matrix(full_grams_minor, dist_only=True, normalize=True, percent=True)
major_bigrams = transition_matrix(full_grams_major, dist_only=True, normalize=True, percent=True)
```

```{code-cell} ipython3
plot_bigram_tables(major_unigrams_norm, minor_unigrams_norm, major_bigrams, minor_bigrams, top=25, two_col_width=12, frequencies=True)
save_pdf_path = os.path.join(RESULTS_PATH, 'bass_degree_bigrams.pdf')
plt.savefig(save_pdf_path, dpi=400)
plt.show()
```

#### Most frequent 2-grams

Select number of first k transitions to display:

```{code-cell} ipython3
k = 25
```

##### Major

```{code-cell} ipython3
sorted_gram_counts(full_grams_major, 2)
```

##### Minor

```{code-cell} ipython3
sorted_gram_counts(full_grams_minor, 2)
```

#### Most frequent 3-grams

##### Major

```{code-cell} ipython3
sorted_gram_counts(full_grams_major, 3)
```

##### Minor

```{code-cell} ipython3
sorted_gram_counts(full_grams_minor, 3)
```

#### Most frequent 4-grams

##### Major

```{code-cell} ipython3
sorted_gram_counts(full_grams_major, 4)
```

##### Minor

```{code-cell} ipython3
sorted_gram_counts(full_grams_minor, 4)
```

#### Most frequent 5-grams

##### Major

```{code-cell} ipython3
sorted_gram_counts(full_grams_major, 5)
```

##### Minor

```{code-cell} ipython3
sorted_gram_counts(full_grams_minor, 5)
```

```{code-cell} ipython3

```