from django.db import models
from django.contrib.gis.db import models

class event(models.Model):
    number = models.CharField("Glide Number",max_length=120)
    event = models.TextField("Event",null=False)
    comment = models.TextField("Comment",null=False)
    the_geom = models.MultiPolygonField()
    
    objects = models.GeoManager()

    def __unicode__(self):
        return self.number

    class Meta:
        verbose_name_plural = "Events"