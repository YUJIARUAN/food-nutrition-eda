from pathlib import Path
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
FIG=ROOT/'results'/'figures'; TAB=ROOT/'results'/'tables'
FIG.mkdir(parents=True,exist_ok=True);TAB.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(ROOT/'data'/'usda_foundation_2026.zip') as z:
    def read(name):
        entry=next(n for n in z.namelist() if n.endswith('/'+name+'.csv'))
        return pd.read_csv(z.open(entry),low_memory=False)
    foods=read('food'); cat=read('food_category'); fn=read('food_nutrient')
foods=foods[foods['data_type']=='foundation_food'].copy()
foods=foods.merge(cat[['id','description']].rename(columns={'id':'food_category_id','description':'category'}),on='food_category_id',how='left')
ids={1008:'energy_direct',2047:'energy_general',2048:'energy_specific',1003:'protein_g',1004:'fat_g',1005:'carbohydrate_g',1063:'sugar_g',1079:'fiber_g',1093:'sodium_mg'}
fn=fn[fn['fdc_id'].isin(foods['fdc_id']) & fn['nutrient_id'].isin(ids)].copy();fn['name']=fn['nutrient_id'].map(ids)
pivot=fn.pivot_table(index='fdc_id',columns='name',values='amount',aggfunc='mean')
df=foods[['fdc_id','description','category']].merge(pivot,on='fdc_id',how='left')
for col in ['energy_direct','energy_general','energy_specific']:
    if col not in df: df[col]=np.nan
# The energy-source field records the USDA method used for every observation.
df['energy_source']=np.select([df['energy_direct'].notna(),df['energy_general'].notna(),df['energy_specific'].notna()],['1008 direct','2047 Atwater general','2048 Atwater specific'],default='missing')
df['energy_kcal']=df['energy_direct'].combine_first(df['energy_general']).combine_first(df['energy_specific'])
cols=['energy_kcal','protein_g','fat_g','carbohydrate_g','sugar_g','fiber_g','sodium_mg']
for c in cols:
    if c not in df: df[c]=np.nan
df.to_csv(TAB/'food_nutrients_clean.csv',index=False)
df[cols].describe().T.to_csv(TAB/'nutrient_summary.csv')
comp=df[cols].notna().mean().sort_values()*100
fig,ax=plt.subplots(figsize=(8,5));ax.barh(comp.index,comp.values);ax.set(xlim=(0,105),xlabel='Availability (%)',title='Nutrient Data Completeness');fig.tight_layout();fig.savefig(FIG/'data_completeness.png',dpi=220);plt.close(fig)
top=df.dropna(subset=['protein_g']).nlargest(15,'protein_g').iloc[::-1]
fig,ax=plt.subplots(figsize=(11,7));ax.barh(top['description'].str.slice(0,50),top['protein_g']);ax.set(xlabel='Protein (g per 100 g)',title='Top 15 Foods by Protein Content');fig.tight_layout();fig.savefig(FIG/'top_protein_foods.png',dpi=220);plt.close(fig)
scatter=df.dropna(subset=['energy_kcal','fat_g']);fig,ax=plt.subplots(figsize=(8,6));ax.scatter(scatter['fat_g'],scatter['energy_kcal'],alpha=.65);ax.set(xlabel='Fat (g / 100 g)',ylabel='Energy (kcal / 100 g)',title='Fat and Energy in Foundation Foods');fig.tight_layout();fig.savefig(FIG/'energy_vs_fat.png',dpi=220);plt.close(fig)
corr=df[cols].corr();fig,ax=plt.subplots(figsize=(8,7));im=ax.imshow(corr.values,cmap='coolwarm',vmin=-1,vmax=1)
ax.set_xticks(range(len(cols)),cols,rotation=90);ax.set_yticks(range(len(cols)),cols)
for i in range(len(cols)):
    for j in range(len(cols)): ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(FIG/'nutrient_correlation_heatmap.png',dpi=220);plt.close(fig)
counts=df.dropna(subset=['protein_g']).groupby('category').size().sort_values(ascending=False)
valid=counts[counts>=10].head(8).index.tolist(); groups=[df.loc[df['category']==c,'protein_g'].dropna() for c in valid]
fig,ax=plt.subplots(figsize=(11,6));ax.boxplot(groups,tick_labels=valid,showfliers=False);ax.tick_params(axis='x',labelrotation=35);plt.setp(ax.get_xticklabels(),ha='right');ax.set(ylabel='Protein (g per 100 g)',title='Protein Distribution by Food Category');fig.tight_layout();fig.savefig(FIG/'protein_by_category_boxplot.png',dpi=220);plt.close(fig)
means=df.groupby('category')[['protein_g','fat_g','carbohydrate_g']].mean().loc[valid[:6]];means.to_csv(TAB/'category_macronutrients.csv')
fig,ax=plt.subplots(figsize=(11,6));x=np.arange(len(means));w=.26
for i,(name,offset) in enumerate([('protein_g',-w),('fat_g',0),('carbohydrate_g',w)]):ax.bar(x+offset,means[name],w,label=name.replace('_g',''))
ax.set_xticks(x,means.index,rotation=35,ha='right');ax.set(ylabel='Mean g per 100 g',title='Macronutrients by Food Category');ax.legend();fig.tight_layout();fig.savefig(FIG/'macronutrient_by_category.png',dpi=220);plt.close(fig)
print('Foundation food records:',len(df),'Categories:',df['category'].nunique())
print('Nutrient availability (%):\n',(df[cols].notna().mean()*100).round(1).to_string())
print(f'Completed. Open {FIG}')
