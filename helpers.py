import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
plt.style.use('ggplot')
from scipy.stats import entropy
import seaborn as sns

def plot_bigram_tables(major_unigrams, minor_unigrams, major_bigrams, minor_bigrams, top, savefig, two_col_width=1, frequencies=False):

    if isinstance(major_unigrams, pd.core.frame.DataFrame):
        major_unigrams = major_unigrams.iloc[:, 0]
    if isinstance(minor_unigrams, pd.core.frame.DataFrame):
        minor_unigrams = minor_unigrams.iloc[:, 0]
    # set custom context for this plot
    with plt.rc_context({
        # disable spines for entropy bars
        'axes.spines.top': False,
        'axes.spines.left': False,
        'axes.spines.bottom': False,
        'axes.spines.right': False,
        'font.family':'sans-serif',
    }):
        # settings for margins etc.
        barsize = [.0, .7]
        gridspec_ratio = [.25, 2.]
        top_margin = .99
        bottom_margin = .12
        hspace = None
        wspace = .0
        right_margin =.005
        left_margin = .085


        fig = plt.figure(figsize=(two_col_width,two_col_width*0.5))

        ### MAJOR BIGRAMS

        gs1 = gridspec.GridSpec(1, 2, width_ratios=gridspec_ratio)
        gs1.update(left=left_margin,
                  right=.5-right_margin,
                  wspace=wspace,
                  hspace=hspace,
                  bottom=bottom_margin,
                  top=top_margin)

        ax1 = plt.subplot(gs1[0, 0])

        vmin = 0
        vmax = 5

        s_maj = pd.Series(
            (major_bigrams.apply(lambda x: entropy(x, base=2), axis=1) / np.log2(major_bigrams.shape[0]))[:top].values,
            index=[
                i + f" ({str(round(fr*100, 1))})" if frequencies else i
                for i,fr in zip(major_bigrams.index[:top], major_unigrams.values[:top])
            ]
        )
        ax = s_maj.plot(kind='barh', ax=ax1, color='k')

        # create a list to collect the plt.patches data
        totals_maj = []
        # find the values and append to list
        for i in ax.patches:
            totals_maj.append(round(i.get_width(), 2))

        for i, p in enumerate(ax.patches):
            # entropy values
            ax1.text(
                totals_maj[i]-0.01,
                p.get_y()+0.3,
                f'${totals_maj[i]}$',
                color='w',
                fontsize=4,
                verticalalignment='center',
                horizontalalignment='left'
            )
        ax1.set_xlim(barsize)
        ax1.invert_yaxis()
        ax1.invert_xaxis()
        ax1.set_xticklabels([])
        ax1.tick_params(
            axis='both',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,
            bottom=False,
            labelleft=True
        )

        ax2 = plt.subplot(gs1[0,1])

        sns.heatmap(major_bigrams[major_bigrams>0].iloc[:top, :top], # only display non-zero values
                    annot=True,
                    fmt='.1f',
                    cmap='Blues',
                    ax=ax2,
                    #vmin=vmin,
                    #vmax=vmax,
                    annot_kws={
                        'fontsize':6.5,
                        'rotation':60
                    },
                    cbar=False,
                   )
        ax2.set_yticks([])
        ax2.tick_params(bottom=False)

        ### MINOR BIGRAMS

        gs2 = gridspec.GridSpec(1, 2, width_ratios=gridspec_ratio)
        gs2.update(left=.5+left_margin,
                  right=1.-right_margin,
                  wspace=wspace,
                  hspace=hspace,
                  bottom=bottom_margin,
                  top=top_margin)

        ax3 = plt.subplot(gs2[0, 0])

        s_min = pd.Series(
            (minor_bigrams.apply(lambda x: entropy(x, base=2), axis=1) / np.log2(minor_bigrams.shape[0]))[:top].values,
            index=[
                i  + f" ({str(round(fr*100, 1))})" if frequencies else i
                for i,fr in zip(minor_bigrams.index, minor_unigrams[:top].values) ])
        ax = s_min.plot(kind='barh', ax=ax3, color='k')

        # create a list to collect the plt.patches data
        totals_min = []

        # find the values and append to list
        for i in ax.patches:
            totals_min.append(round(i.get_width(), 2))

        for i, p in enumerate(ax.patches):
            ax3.text(
                totals_min[i]-0.01,
                p.get_y()+0.3,
                f'${totals_min[i]}$',
                color='w',
                fontsize=4,
                verticalalignment='center',
                horizontalalignment='left'
            )
        ax3.set_xlim(barsize)

        ax3.invert_yaxis()
        ax3.invert_xaxis()
        ax3.set_xticklabels([])
        ax3.tick_params(
            axis='both',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left=False,      # ticks along the bottom edge are off
            right=False,
            bottom=False,
            labelleft=True
        )

        ax4 = plt.subplot(gs2[0, 1])

        sns.heatmap(minor_bigrams[minor_bigrams>0].iloc[:top, :top], # only display non-zero values
                    annot=True,
                    fmt='.1f',
                    cmap='Reds',
                    ax=ax4,
                    #vmin=vmin,
                    #vmax=vmax,
                    annot_kws={
                        'fontsize':6.5,
                        'rotation':60
                    },
                    cbar=False,
                   )

        ax4.set_yticks([])
        ax4.tick_params(bottom=False)

        fig.align_labels()
        name = 'bigrams.pdf'
        if savefig:
            plt.savefig(name, dpi=400)
        plt.show()
    return fig



def nest_level(obj, include_tuples=False):
    """Recursively calculate the depth of a nested list.

    """
    if obj.__class__ != list:
        if include_tuples:
            if obj.__class__ != tuple:
                return 0
        else:
            return 0
    max_level = 0
    for item in obj:
        max_level = max(max_level, nest_level(item, include_tuples=include_tuples))
    return max_level + 1

def grams(l, n=2):
    """Returns a list of n-gram tuples for given list. List can be nested.

    Use nesting to exclude transitions between pieces or other units.

    """
    if nest_level(l) > 1:
        ngrams = []
        no_sublists = []
        for item in l:
            if isinstance(item,list):
                ngrams.extend(grams(item,n))
            else:
                no_sublists.append(item)
        if len(no_sublists) > 0:
            ngrams.extend(grams(no_sublists,n))
        return ngrams
    else:
        #if len(l) < n:
        #    print(f"{l} is too small for a {n}-gram.")
        #ngrams = [l[i:(i+n)] for i in range(len(l)-n+1)]
        ngrams = list(zip(*(l[i:] for i in range(n))))
        # convert to tuple of strings
        return [tuple(str(g) for g in gram) for gram in ngrams]


def transition_matrix(l=None, gs=None, n=2, k=None, smooth=0, normalize=False, IC=False, filt=None, dist_only=False,sort=False, percent=False, decimals=None):
    """Returns a transition table from a list of symbols.

    Column index is the last item of grams, row index the n-1 preceding items.

    Parameters
    ----------

    l: list, optional
        List of elements between which the transitions are calculated.
        List can be nested.
    gs: list, optional
        List of tuples being n-grams
    n: int, optional
        get n-grams
    k: int, optional
        Number of rows and columns that you want to keep
    smooth: number, optional
        initial count value of all transitions
    normalize: bool, optional
        set True to divide every row by the sum of the row.
    IC: bool, optional
        Set True to calculate information content.
    filt: list, optional
        elements you want to exclude from the table. All ngrams containing at least one
        of the elements will be filtered out.
    dist_only: bool, optional
        if True, n-grams consisting only of identical elements are filtered out
    sort : bool, optional
        By default, the indices are ordered by gram frequency. Pass True to sort
        by bigram counts.
    percent : bool, optional
        Pass True to multiply the matrix by 100 before rounding to `decimals`
    decimals : int, optional
        To how many decimals you want to round the matrix.
    """
    if gs is None:
        assert (n>0), f"Cannot print {n}-grams"
        gs = grams(l, n=n)
    elif l is not None:
        assert True, "Specify either l or gs, not both."

    if filt:
        gs = list(filter(lambda n: not any(g in filt for g in n),gs))
    if dist_only:
        gs = list(filter(lambda tup: any(e != tup[0] for e in tup),gs))
    ngrams = pd.Series(gs).value_counts()
    ngrams.index = [(' '.join(t[:-1]),t[-1]) for t in ngrams.index.tolist()]
    context = pd.Index(set([ix[0] for ix in ngrams.index]))
    consequent = pd.Index(set([ix[1] for ix in ngrams.index]))
    df = pd.DataFrame(smooth, index=context, columns=consequent)


    for i, (cont, cons) in enumerate(ngrams.index):
        try:
            df.loc[cont, cons] += ngrams[i]
        except:
            continue



    if k is not None:
        sort=True

    if sort:
        h_sort = list(df.max().sort_values(ascending= False).index.values)
        v_sort = list(df.max(axis=1).sort_values(ascending= False).index.values)
        df = df[h_sort].loc[v_sort]
    else:
        frequency = df.sum(axis=1).sort_values(ascending=False).index
        aux_index = frequency.intersection(df.columns, sort=False)
        aux_index = aux_index.union(df.columns.difference(frequency, sort=False), sort=False)
        df = df[aux_index].loc[frequency]

    SU = df.sum(axis=1)
    if normalize or IC:
        df = df.div(SU,axis=0)

    if IC:
        ic = np.log2(1/df)
        ic['entropy'] = (ic * df).sum(axis=1)
        ############## Identical calucations:
        #ic['entropy2'] = scipy.stats.entropy(df.transpose(),base=2)
        #ic['entropy3'] = -(df * np.log2(df)).sum(axis=1)
        df = ic
        if normalize:
            df['entropy'] = df['entropy'] / np.log2(len(df.columns)-1)
    # else:
    #     df['total'] = SU

    if k is not None:
        df = df.iloc[:k, :k]

    if percent:
        df.iloc[:,:-1] *= 100

    if decimals is not None:
        df = df.round(decimals)

    return df