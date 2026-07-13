// ------------------------------------------------------------------
// Panel dataset: NDVI (Sentinel-2) and real precipitation (PRISM)
// for Georgia's top cotton-producing counties by 2023 NASS acreage,
// growing seasons 2019-2024
//
// NOTE: PRISM's AN81m collection ends December 2020; the successor
// AN91m collection begins January 2021. We merge both to cover the
// full 2019-2024 study period.
//
// Run this at code.earthengine.google.com, then export the result
// (Tasks tab) to Google Drive as ndvi_precip_panel.csv, and place it
// in data/ to reproduce the analysis in src/.
// ------------------------------------------------------------------

var countyNames = ['Dooly','Colquitt','Worth','Mitchell','Bulloch','Crisp',
                    'Brooks','Wilcox','Coffee','Irwin','Turner','Berrien'];

var counties = ee.FeatureCollection("TIGER/2018/Counties")
  .filter(ee.Filter.eq('STATEFP', '13'))
  .filter(ee.Filter.inList('NAME', countyNames));

print('Counties selected:', counties.size());

var years = ee.List.sequence(2019, 2024);

function maskS2clouds(image) {
  var qa = image.select('QA60');
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  return image.updateMask(mask).divide(10000);
}

// Merge PRISM's two collections to cover the full study period
var prismLegacy = ee.ImageCollection('OREGONSTATE/PRISM/AN81m');
var prismCurrent = ee.ImageCollection('OREGONSTATE/PRISM/AN91m');
var prism = prismLegacy.merge(prismCurrent);

var yearlyFeatures = years.map(function(y) {
  y = ee.Number(y);
  var start = ee.Date.fromYMD(y, 4, 1);
  var end = ee.Date.fromYMD(y, 9, 30);

  var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate(start, end)
    .filterBounds(counties)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(maskS2clouds);
  var ndvi = s2.median().normalizedDifference(['B8','B4']).rename('NDVI');

  var precip = prism.filterDate(start, end).select('ppt').sum().rename('precip_mm');

  var combined = ndvi.addBands(precip);

  var stats = combined.reduceRegions({
    collection: counties,
    reducer: ee.Reducer.mean(),
    scale: 30
  });

  return stats.map(function(f) { return f.set('year', y); });
});

var panel = ee.FeatureCollection(yearlyFeatures).flatten();

print('Panel size (should be ~72):', panel.size());
print('Sample rows:', panel.limit(5));

Export.table.toDrive({
  collection: panel,
  description: 'ndvi_precip_panel_nass_counties_2019_2024',
  fileFormat: 'CSV',
  selectors: ['NAME','year','NDVI','precip_mm']
});
