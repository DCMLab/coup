from ms3 import Parse
from ms3.utils import transform, roman_numeral2tpc, fifths2pc
import pandas as pd
dir = '/home/hentsche/ABC/harmonies'
p = Parse(dir, file_re='tsv$', index='fname')
p.parse()
p
cl = p.get_labels()
cl

transpose_by = transform(cl, roman_numeral2tpc, ['localkey', 'globalkey_is_minor'])
bass = cl.bass_note + transpose_by
bass
ivs = bass - bass.shift()
ivs.value_counts()

pc_ivs = fifths2pc(ivs)
pc_ivs.index = cl.index
pc_ivs = pc_ivs.where(pc_ivs <= 6, pc_ivs % -6).fillna(0)
pc_ivs.value_counts()


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

desc = cnt(pc_ivs, -1)
desc.n.value_counts()

cl.loc[three_desc[0]]


desc = pc_ivs == -1
desc.where(desc, np.nan).ffill(limit=2).fillna(False).astype(bool)
three_desc = ~desc & desc.shift(1) & desc.shift(2)

cl[three_desc.where(three_desc, np.nan).ffill(limit=2).fillna(False).astype(bool)]
pc_ivs[pc_ivs==-1]


from ms3.expand_dcml import chord2tpcs, changes2list
chord2tpcs('ii6(11b6#7)', merge_tones=True)
chord2tpcs('ii65(#7)', merge_tones=False)
any((True, True, True))

2 == 2 != 3

acc = 'b'
acc.count('#') - acc.count('b')
# moz_dir = '/home/hentsche/Documents/Code/ms3_development/moppel'
# cad_dir = '/home/hentsche/Documents/Code/ms3_development/moppel/cadences'
# log_dir = '/home/hentsche/Documents/Code/ms3_development/moppel/logs'
# l = '../test.log'
# p = Parse(moz_dir, key='moz', logger_cfg=dict(level='i', path=log_dir, file=l))
# p.add_dir(cad_dir, key='cad', file_re='tsv')
# p.parse(label_col='cadence')
# p.detach_labels()
# empty_dir = '/home/hentsche/Documents/Code/ms3_development/moppel/empty'
# p.store_mscx(folder=empty_dir, suffix='_empty')
# p.add_detached_annotations('moz', 'cad')
# p['cad']
# p.attach_labels(annotation_key='cad', staff=1, voice=1)
# l = []
# next(e for e in reversed(l) if e != -1)
# l.insert(-1, 5)
# l
# from ms3 import Score
# f = "/home/hentsche/Documents/Code/ms3_development/c11n08_Rondeau.mscx"
# s = Score(f, logger_cfg={'level': 'd'})
# s.mscx.measures.set_index('mc').next.iloc[:60]
# s.mscx.measures.markers
# s.mscx.parsed._measures['Jump/playRepeats'].value_counts()
# breaks = s.mscx.parsed._measures[['LayoutBreak/subtype', 'mc']].copy()
# breaks.rename(columns={'LayoutBreak/subtype': 'breaks'}, inplace=True)
# breaks.mc.where(breaks.breaks.notna(), None)
# section_breaks = breaks.loc[breaks.breaks == 'section', 'mc'].to_list()
# section_breaks = [0] + section_breaks + [breaks.mc.max()]



from ms3.utils import next2sequence
next2sequence(s.mscx.measures.set_index('mc').next)

split_alternatives(s.mscx.labels)
regex = r"-(?!(#+|b+)?\d)"
spl = s.mscx.labels.label.str.split(regex, expand=True)
s.logger.logger.file_handler.baseFilename
s.__getattribute__('fnames')
s.logger.logger.file_handler = s.logger.logger.handlers[1]
from ms3.expand_dcml import split_alternatives
import os
os.path.join('hi', None)
os.path.split('..')
os.path.splitext('hallo')
chord2tpcs('ii%65(-1)/vi')
a = [2,4,6]
a.insert(0, 1)
a.insert(-1, 10)
a.replace(2, 3)
a.remove(4)
a
