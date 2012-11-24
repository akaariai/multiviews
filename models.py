from django.db import models
class SingleField(models.Model):
    f = models.TextField()

    def __unicode__(self):
        return self.f

    class Meta:
        ordering = ('f',)

class MultiField(models.Model):
    f1 = models.TextField()
    f2 = models.TextField()
    f3 = models.TextField()
    f4 = models.TextField()
    f5 = models.TextField()
    f6 = models.TextField()
    f7 = models.TextField()
    f8 = models.TextField()
    f9 = models.TextField()
    f10 = models.TextField()

    def __unicode__(self):
        return self.f1

    class Meta:
        ordering = ('f1',)
