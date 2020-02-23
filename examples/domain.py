
from cordex import domain as dm

domains = dm.domains()
print('available domains: {}'.format(domains))

for short_name in domains:
    print('creating domain: {}'.format(short_name))
    domain = dm.domain(short_name)
    domain.to_netcdf(short_name+'.nc', dummy='topo')
