import pandas as pd
import pylab as pl
import seaborn as sbs
sbs.set()
sbs.set_context('talk')

df = pd.read_csv('examples/treatment_options_single_disease.tsv', sep='\t')
df.loc[:, 'color'] = df['Testing and treatment strategy'].apply(lambda r: 'rational' if r in ['baseline(no testing)','A','F','H','I','B'] else 'dominated')
print(df); 
fig, ax = pl.subplots()
ax = sbs.scatterplot(df,y='Cost{$}',x='Effectiveness{QALYs gained}',hue='color', size='color', sizes=(20,40), markers=['o','x'])
#ax = sbs.pointplot(df,y='Cost{$}',x='Effectiveness{QALYs gained}',hue='color', markers=['o','x'],linestyle='none')
ax = sbs.lineplot(df,y='Cost{$}',x='Effectiveness{QALYs gained}',hue='color', size='color', sizes=(1,2), linestyle=':', legend=False)
for i, row in df.iterrows():
    ax.annotate(row['Testing and treatment strategy'], [row['Effectiveness{QALYs gained}'], row['Cost{$}']],fontsize=11) 
pl.show()
