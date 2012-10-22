# Bottom, Left, Top, Right
# South, West, North, East

# Valid TypeName's http://www.gdal.org/ogr/drv_osm.html
# * points
# * lines
# * multilinestrings
# * multipolygons
# * other_relations

# All Points in Oceanside, CA
curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:points&bbox=33.149559,-117.437447,33.304920,-117.209473"

# All LineStrings in Barranquilla, Colombia

curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:lines&bbox=10.903130,-74.835899,11.019240,-74.741623" 

# All Multilinestrings in Körmend, Hungary

curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:multilinestrings&bbox=46.977859,16.572309,47.043941,16.638390" 

# All multipolygons in Yogyakarta, Indonesia

curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:multipolygons&bbox=-7.8360,110.3883,-7.7649,110.3395"

# All "other_relations" around Shinjuku, Tokyo, Japan
# (Will almost certainly time out)

curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:other_relations&bbox=35.6731,139.7453,139.6733,35.7299"

# All Multipolygons in the Tijuana River Valley

curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:multipolygons&bbox=32.5043,-117.1247,32.5225,-117.1031"

# All LineStrings in Monterrey, California

curl "http://vgi.dev.opengeo.org/osm_wfs/?service=wfs&request=GetFeature&version=2.0.0&typename=osm:lines&bbox=36.5714,-121.9264,36.6187,-121.8081"
