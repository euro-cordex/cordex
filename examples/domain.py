from cordex import domain as dm

# available tables
print(dm.tables())
# print cordex core table
print(dm.table('cordex-core'))
# available domains
print(dm.domains())
# available domains in cordex-core
print(dm.domains('cordex-core'))

# create domains with some dummy data (uses cdo topo)
for short_name in dm.domains():
    print('creating domain: {}'.format(short_name))
    domain = dm.domain(short_name)
    print(domain)
    domain.to_netcdf(short_name+'.nc', dummy='topo')
