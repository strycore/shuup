# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2017, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import logging
from django.forms import ModelChoiceField
from filer.fields.file import AdminFileWidget

from shuup.admin.forms.widgets import FileDnDUploaderWidget
from shuup.admin.utils.permissions import user_has_permission
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm

LOGGER = logging.getLogger(__name__)
MAX_RECOMMENDED_CHOICES = 100


class ShuupAdminForm(MultiLanguageModelForm):

    def __init__(self, **kwargs):
        super(ShuupAdminForm, self).__init__(**kwargs)
        for field in self.fields:
            actual_field = self.fields[field]
            if issubclass(actual_field.widget.__class__, AdminFileWidget):
                actual_field.widget = FileDnDUploaderWidget(
                    upload_path="/default", kind="images", clearable=True)

            if issubclass(actual_field.__class__, ModelChoiceField):
                request = getattr(self, "request", None)
                if not request:
                    return
                user = getattr(self.request, "user", None)
                if not user:
                    return

                choices_count = actual_field.queryset.count()
                if choices_count > MAX_RECOMMENDED_CHOICES:
                    LOGGER.warning("Field %s in %s has %d choices, this might slow down the view",
                                   actual_field.label, self.__class__.__name__, choices_count)
                actual_field.widget.choices = [
                    (item.pk, item) for item in actual_field.queryset
                    if user_has_permission("view", self.request.user, item)
                ]
