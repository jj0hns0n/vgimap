from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.geos import Point

from ga_ows.views.wfs import WFSAdapter, FeatureDescription

from vgimap.services.models import Service
from vgimap.services.models import TwitterTweet, TwitterPlace
from vgimap.services.models import UshahidiReport, UshahidiCategory
from vgimap.services.models import OsmNode, OsmWay, OsmNodeTag

import os
import json
import datetime
import requests
import twitter
import OsmApi
import ogr

from uuid import uuid4
from urlparse import urljoin
from tempfile import gettempdir

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
        self.service = Service.objects.filter(type='OSM')[0]

    def get_feature_descriptions(self, request, **params):
        namespace = request.build_absolute_uri().split('?')[0] + "/schema"
        extent = (-180,-90,180,90)

        return [FeatureDescription(
                ns=namespace,
                ns_name="osm",
                name="OpenStreetMap",
                abstract="OpenStreetMap Data",
                title="OpenStreetMap Data",
                keywords=['openstreetmap', 'osm', 'vgi'],
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
            data  = self.osm_api._get("/api/interpreter?data=node%5B%22highway%22%3D%22bus%5Fstop%22%5D%5B%22shelter%22%5D%5B%22shelter%22%21%7E%22no%22%5D%2850%2E7%2C7%2E1%2C50%2E8%2C7%2E25%29%3Bout%20meta%3B")
            #data = api.ParseOsm(data)
            tmpname = "{tmpdir}{sep}{uuid}.{output_format}".format(tmpdir=gettempdir(), uuid=uuid4(), output_format='osm', sep=os.path.sep)
            f = open(tmpname, 'w')
            f.write(data)
            f.close()
            ds = ogr.Open(tmpname)
            print ds
            return ds
        else:
            pass

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
        
            api = twitter.Api()
            if 'user' in flt_dict:
                statuses = api.GetUserTimeline(flt_dict['user'])
            else:
                statuses = api.GetPublicTimeline() 
            status_ids = []
            # Cache to the Database
            for s in statuses:
                try:
                    tweet = TwitterTweet.objects.get(identifier=s.id)
                except ObjectDoesNotExist:
                    tweet = TwitterTweet()
                    tweet.save_tweet(s)
                status_ids.append(tweet.identifier)

            # Look back up in the DB and return the results
            return TwitterTweet.objects.filter(identifier__in=status_ids) # TODO Slice for paging
        else:
            return TwitterTweet.objects.all() # TODO slice for paginl


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
