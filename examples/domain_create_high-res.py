"""Create high-res domains from cordex 0.44 domains.
"""


from cordex import domain as dm
import pandas as pd

df = pd.DataFrame()

# create high-res domains from cordex domains
for short_name in dm.domains('cordex'):
    print('creating domain: {}'.format(short_name))
    cordex_domain = dm.domain(short_name)
    if cordex_domain.dlon == 0.44:
        high_res = cordex_domain * 0.25
        high_res.short_name = cordex_domain.short_name.split('-')[0]+'-11'
        high_res.long_name = cordex_domain.long_name
        high_res.region = cordex_domain.region
        df = df.append(high_res.to_pandas(), ignore_index=True)


print(dm.table('cordex'))
print(df)
df.to_csv('cordex-high-res.csv', index=False, float_format='%g')
