from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property


class BaseModelMixin(models.Model):
    """Base model mixin that should be applied for all model classes"""

    objects = models.Manager()

    @cached_property
    def admin_url(self):
        if not self.id:
            return None
        obj_path = reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=[self.id],
        )
        return obj_path

    class Meta:
        abstract = True
