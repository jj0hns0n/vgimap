from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point

from ga_ows.views.wfs import WFSAdapter, FeatureDescription

from vgimap.services.models import Service
from vgimap.services.models import TwitterTweet, TwitterPlace
from vgimap.services.models import UshahidiReport, UshahidiCategory
from vgimap.services.models import OsmNode, OsmWay, OsmNodeTag

import os
import sys
import json
import datetime
import requests
import twitter
import OsmApi
from osgeo import ogr

from lxml import etree
from uuid import uuid4
from urlparse import urljoin
from tempfile import gettempdir
import urllib

def get_response(url):
    "This hits the api identified by the service and returns the response"
    try:
        req = requests.get(url)
        return req
    except requests.exceptions.ConnectionError, e:
        return e


class OSMWFSAdapter(WFSAdapter):

    def __init__(self):
        self.osm_api = OsmApi.OsmApi(api = "www.overpass-api.de")
        #self.service = Service.objects.filter(type='OSM')[0]

    def get_feature_descriptions(self, request, **params):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema"
        extent = (-180,-90,180,90)

        return [
                FeatureDescription(
                    ns=namespace,
                    ns_name="osm",
                    name="points",
                    abstract="OpenStreetMap Point Data",
                    title="OpenStreetMap Point Data",
                    keywords=['openstreetmap', 'osm', 'vgi'],
                    srs="EPSG:4326",
                    bbox=[-180,-90,180,90],
                    schema=namespace),
                FeatureDescription(
                    ns=namespace,
                    ns_name="osm",
                    name="lines",
                    abstract="OpenStreetMap Line Data",
                    title="OpenStreetMap Line Data",
                    keywords=['openstreetmap', 'osm', 'vgi'],
                    srs="EPSG:4326",
                    bbox=[-180,-90,180,90],
                    schema=namespace),
                FeatureDescription(
                    ns=namespace,
                    ns_name="osm",
                    name="multipolygons",
                    abstract="OpenStreetMap MultiPolygon Data",
                    title="OpenStreetMap MultiPolygon Data",
                    keywords=['openstreetmap', 'osm', 'vgi'],
                    srs="EPSG:4326",
                    bbox=[-180,-90,180,90],
                    schema=namespace),
                FeatureDescription(
                    ns=namespace,
                    ns_name="osm",
                    name="multilinestrings",
                    abstract="OpenStreetMap Multilinestring Data",
                    title="OpenStreetMap Line Data",
                    keywords=['openstreetmap', 'osm', 'vgi'],
                    srs="EPSG:4326",
                    bbox=[-180,-90,180,90],
                    schema=namespace),
                FeatureDescription(
                    ns=namespace,
                    ns_name="osm",
                    name="other_relations",
                    abstract="OpenStreetMap Other Relations Data",
                    title="OpenStreetMap Line Data",
                    keywords=['openstreetmap', 'osm', 'vgi'],
                    srs="EPSG:4326",
                    bbox=[-180,-90,180,90],
                    schema=namespace),
            ]

    def list_stored_queries(self, request):
        pass

    def get_features(self, request, params):
        # Can eventually support stored queries here
        return self.AdHocQuery(request, params)

    def AdHocQuery(self, request, params):
        type_names = params.cleaned_data['type_names'] # only support one type-name at a time (model) for now
        flt = params.cleaned_data['filter'] # filter should be in JSON 
        bbox = params.cleaned_data['bbox']
        if bbox == (-180,-90,180,90): 
            bbox = [-0.1,-0.1,0.1,0.1]
        sort_by = params.cleaned_data['sort_by']
        count = params.cleaned_data['count']
        if not count:
            count = params.cleaned_data['max_features'] 
        start_index = params.cleaned_data['start_index']
        srs_name = params.cleaned_data['srs_name'] # assume bbox is in this
        srs_format = params.cleaned_data['srs_format'] # this can be proj, None (srid), srid, or wkt.
       
        if bbox:
            query = str("(node(%f,%f,%f,%f);<;>;);out meta;" % (bbox[0], bbox[1], bbox[2], bbox[3]))
        if flt:
            # Parse the query
            # Convert to Overpass API Params
            # Execute the query against the Overpass API
            pass

        url = str("/api/interpreter?data=" + urllib.quote_plus(query))
        data = self.osm_api._get(url)

        # Write the results out to a temp file
        tmpname = "{tmpdir}{sep}{uuid}.{output_format}".format(tmpdir=gettempdir(), uuid=uuid4(), output_format='osm', sep=os.path.sep)
        f = open(tmpname, 'w')
        f.write(data)
        f.close()
        return (tmpname, str(type_names[0].split(':')[1]))
            

class TwitterWFSAdapter(WFSAdapter):

    def __init__(self):
        pass

    def get_feature_descriptions(self, request, **params):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema"
        extent = (-180,-90,180,90)

        return [FeatureDescription(
                ns=namespace,
                ns_name="tweets",
                name="tweets",
                abstract="twitter tweets",
                title="twitter tweets",
                keywords=[],
                srs="EPSG:4326",
                bbox=[-180,-90,180,90],
                schema=namespace
            )]     

    def list_stored_queries(self, request):
        pass

    def get_features(self, request, params):
        # Can eventually support stored queries here
        return self.AdHocQuery(request, params)

    def AdHocQuery(self, request, params):
        type_names = params.cleaned_data['type_names'] # only support one type-name at a time (model) for now
        flt = params.cleaned_data['filter']
        bbox = params.cleaned_data['bbox'] 
        sort_by = params.cleaned_data['sort_by']
        count = params.cleaned_data['count']
        if not count:
            count = params.cleand_data['max_features'] 
        start_index = params.cleaned_data['start_index']
        srs_name = params.cleaned_data['srs_name'] # assume bbox is in this
        srs_format = params.cleaned_data['srs_format'] # this can be proj, None (srid), srid, or wkt.
       
        flt_dict = {}
        search_terms = []
        if flt:
            try:
                flt = flt.replace('ogc:', '').replace('gml:', '')
                flt_tree = etree.fromstring(flt)
                # Parse out search terms
                for prop in flt_tree.findall('.//PropertyIsLike'):
                    search_terms.append(prop.find('.//Literal').text)
                # Parse out bbox
            except:
                print "Unexpected error:", sys.exc_info()[0] 
        else:
            pass

        api = twitter.Api()
        if len(search_terms) > 0:
            statuses = api.GetSearch(term=(' '.join(search_terms)))
        elif 'user' in flt_dict:
            statuses = api.GetUserTimeline(flt_dict['user'])
        else:
            statuses = api.GetSearch(term="sandy", geocode=(34.0522, -118.2436, '10km'))
        status_ids = []
        # Cache to the Database
        for s in statuses:
            tweet = TwitterTweet()
            tweet.save_tweet(s)
            status_ids.append(tweet.identifier)

        # Look back up in the DB and return the results
        return TwitterTweet.objects.filter(identifier__in=status_ids) # TODO Slice for paging


class UshahidiWFSAdapter(WFSAdapter):

    def __init__(self):
        pass

    def get_feature_descriptions(self, request, **params):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema"
        extent = (-180,-90,180,90)

        return [FeatureDescription(
                ns=namespace,
                ns_name="reports",
                name="incidents",
                abstract="ushahidi reports",
                title="ushahidi reports",
                keywords=[],
                srs="EPSG:4326",
                bbox=[-180,-90,180,90],
                schema=namespace
            )]

    def list_stored_queries(self, request):
        pass

    def get_features(self, request, params):
        # Can eventually support stored queries here
        return self.AdHocQuery(request, params)

    def update_categories(self,categories,service):
        created_categories = []
        for category in categories:
            category,created = UshahidiCategory.objects.get_or_create(service=service,category_id=category['category']['id'],category_name=category['category']['title'])
        created_categories.append(category)
        return created_categories

    def AdHocQuery(self, request, params):
        type_names = params.cleaned_data['type_names'] # only support one type-name at a time (model) for now
        flt = params.cleaned_data['filter'] # filter should be in JSON 
        bbox = params.cleaned_data['bbox']
        sort_by = params.cleaned_data['sort_by']
        count = params.cleaned_data['count']
        if not count:
            count = params.cleand_data['max_features']
        start_index = params.cleaned_data['start_index']
        srs_name = params.cleaned_data['srs_name'] # assume bbox is in this
        srs_format = params.cleaned_data['srs_format'] # this can be proj, None (srid), srid, or wkt.

        if flt:
            flt_dict = json.loads(flt)

            if 'service' in flt_dict:
                #we get the service from the db, create it if it does not exists
                service = Service.objects.get(name=flt_dict['service'])
                #ushahidireport = UshahidiReport.objects.get(service__name=flt_dict['service']) #todo create when the service does not exist
                #service = ushahidireport.service
                #we now fetch the reports into a dictionary
                url = urljoin(service.url,'api?task=incidents')
                response = get_response(url)
                data = response.json
                reports = data['payload']['incidents']
            reports_ids = []
            # Cache to the Database
            for incident in reports:
                try:
                    report = UshahidiReport.objects.get(identifier=incident['incident']['incidentid'])
                except ObjectDoesNotExist:
                    right_now = datetime.datetime.utcnow()
                    report = UshahidiReport(service=service,identifier=incident['incident']['incidentid'],incident_mode = incident['incident']['incidentmode']
                             ,created = right_now,incident_active = incident['incident']['incidentactive']
                             ,incident_verified = incident['incident']['incidentverified'],location_id = incident['incident']['locationid']
                             ,text = incident['incident']['incidentdescription'],title = incident['incident']['incidenttitle']
                             ,geom = Point(float(incident['incident']['locationlongitude']), float(incident['incident']['locationlatitude']))
                             ,location_name = incident['incident']['locationname'],person_first = None,person_last = None,person_email = None
                             ,incident_photo = None,incident_video = None,incident_news = None)
                    report.save(report)
                    #import pdb;pdb.set_trace()
                    categories = self.update_categories(incident['categories'],service)
                    report.incident_categories.add(*categories)
                    #report.save(report)
                reports_ids.append(incident['incident']['incidentid'])

            # Look back up in the DB and return the results
            return UshahidiReport.objects.filter(identifier__in=reports_ids) # TODO Slice for paging
        else:
            return UshahidiReport.objects.all() # TODO slice for paging
