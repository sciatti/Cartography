import csv
import geopandas as gpd
import matplotlib.pyplot as plt

wayne_county = {}

tract_file_path = 'CartographyData/tl_2020_26_tract/tl_2020_26_tract.shp'

tract_df = gpd.read_file(tract_file_path)

with open('DECENNIALDHC2020.P1_2023-11-01T220522/DECENNIALDHC2020.P1-Data.csv', 'r', encoding='UTF-8') as data:
    reader = csv.DictReader(data, delimiter=',')
    for row in reader:
        if 'Wayne County' in row['NAME']:
            locationData = row['NAME'].split(';')
            tract_id = locationData[0][locationData[0].find('Tract')+6:]
            tract_id = tract_id.replace('.', '')
            tract_id = tract_id.ljust(6, '0')
            wayne_county[tract_id] = row['P1_001N']

wayne_county_df = tract_df.loc[(tract_df['STATEFP'] == '26') & (tract_df['COUNTYFP'] == '163')]

wayne_county_df = wayne_county_df.to_crs('epsg:3857')
wayne_county_df['area_sq_km'] = wayne_county_df['geometry'].area / 10**6

wayne_county_df['population'] = wayne_county_df['TRACTCE'].apply(lambda x: wayne_county[x])

wayne_county_df['density'] = wayne_county_df['population'].astype(int) / wayne_county_df['area_sq_km']

wayne_county_df['normalized_density'] = (wayne_county_df['density'] - wayne_county_df['density'].min()) / (wayne_county_df['density'].max() - wayne_county_df['density'].min())

wayne_county_df['color'] = wayne_county_df['normalized_density'].apply(lambda d: '#ff0000' + f'{int((d)*255):x}'.zfill(2))

wayne_county_df.plot(color=wayne_county_df['color'], edgecolor='black', linewidth=0.25)
plt.savefig('Wayne_County_Density.png', dpi=800)

