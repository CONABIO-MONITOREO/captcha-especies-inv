from django.db import models


class Photo(models.Model):
    ftrampa_id = models.CharField(max_length=200, null=False, blank=True, db_index=True)
    ruta = models.TextField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)
    fecha_foto = models.DateTimeField(null=True)

    def __str__(self):
        return self.annotation_id

class Annotation(models.Model):
    ftrampa_id = models.CharField(max_length=200, null=False, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    annotation_id = models.CharField(max_length=50, null=False, blank=True, db_index=True)
    p1_x = models.IntegerField(null=True)
    p1_y = models.IntegerField(null=True)
    p2_x = models.IntegerField(null=True)
    p2_y = models.IntegerField(null=True)
    path = models.TextField(null=False, blank=True)
    indexed = models.BooleanField(default=False)

    def __str__(self):
        return self.annotation_id
    

class ParametrizedSpecies(models.Model):
    taxa_id = models.IntegerField(db_index=True, null=True)
    species = models.CharField(max_length=100, null=False, blank=False)
    clase = models.CharField(max_length=100, null=False, blank=True, default='')
    genero = models.CharField(max_length=100, null=False, blank=True, default='')
    orden = models.CharField(max_length=100, null=False, blank=True, default='')
    reino = models.CharField(max_length=100, null=False, blank=True, default='')
    phylum = models.CharField(max_length=100, null=False, blank=True, default='')
    familia = models.CharField(max_length=100, null=False, blank=True, default='')

    def __str__(self):
        return self.species