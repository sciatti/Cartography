import geopandas as gpd
import matplotlib.pyplot as plt
import csv

tract_file_path = 'CartographyData/cb_2018_26_tract_500k/cb_2018_26_tract_500k.shp'
tract_pop_path = 'CartographyData/archive/acs2017_census_tract_data.csv'

tract_df = gpd.read_file(tract_file_path)
tract_dict = {}

mi_state_code = '26'
county_codes = {
    'Wayne County': '163',
    'Oakland County': '125',
    'Macomb County': '099',
    'Washtenaw County': '161'
}

with open(tract_pop_path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tract_dict[row['TractId']] = row

# tract_df.plot()
# plt.savefig('fig.png')
# 26163 is Wayne County's FIPS code
# 26 is michigan's FP code
# 125 is Oakland County's FP code
# 173200 is the tract I live in
# all together: 26125173200 is my TractId in the csv file

my_df = tract_df.loc[(tract_df['STATEFP'] == '26') & (tract_df['COUNTYFP'] == '125') & (tract_df['TRACTCE'] == '173200')]
my_df.plot()

#print(tract_df.loc[tract_df['STATEFP'] == '26'])
#wayne_df = tract_df.loc[(tract_df['COUNTYFP'] == '163') & (tract_df['STATEFP'] == '26')]
#wayne_df = tract_df[tract_df['TRACTCE'].isin(wayne_list)]
#wayne_df.info()
#wayne_df.plot()
plt.savefig('fig.png')

# Counties I will include:
# 1. Wayne - 26163, 1.75 Million people
# 2. Oakland - 26125, 1.269 Million people
# 3. Macomb - 26099, 0.87 Million people
# 4. Washtenaw - 26161, 0.37 Million people
# Total: ~4.25 Million people

# 1. Collect tract geospatial data in dataframe
# 2. Collect population data in csv
# 3. Create county dataframe where only wanted counties are present
# 4. Insert population data in county dataframe
# 5. Calculate area per each tract in each county
# 6. Create density column by dividing population by area to retrieve people/sq km
# 7. Add color column by taking normalized min across density
# 8. Plot

testguy = tract_df.loc[tract_df['COUNTYFP'].isin(list(county_codes.values()))]

# tract_df = tract_df.to_crs('espg:3857')

county_df = tract_df.loc[((tract_df['STATEFP'] == mi_state_code) & (tract_df['COUNTYFP'].isin(list(county_codes.values()))))]

county_df['tract_index'] = county_df['STATEFP'] + county_df['COUNTYFP'] + county_df['TRACTCE']

county_df['population'] = county_df['tract_index'].apply(lambda x: tract_dict[x]['TotalPop'])

cartesian_df = county_df.copy()
cartesian_df = cartesian_df.to_crs('epsg:3857')
cartesian_df['area_sq_km'] = cartesian_df['geometry'].area / 10**6

cartesian_df['density'] = cartesian_df['population'].astype(int) / cartesian_df['area_sq_km'].astype(float)

print(cartesian_df['density'], cartesian_df['density'].max(), cartesian_df['density'].min())

cartesian_df['normalized_density'] = (cartesian_df['density'] - cartesian_df['density'].min()) / (cartesian_df['density'].max() - cartesian_df['density'].min()) 

#print(cartesian_df['normalized_density'])

cartesian_df['color'] = cartesian_df['normalized_density'].apply(lambda d: '#ff0000' + f'{int((d)*255):x}'.zfill(2))

cartesian_df.plot(color=cartesian_df['color'], edgecolor='black', linewidth=0.25)
plt.savefig('Metro_Detroit_Density.png', dpi=800)
