from ArabicTools.constants import MAX_SPELLING_LENGTH, DEFAULT_ROOT_SPELLING
from ArabicTools.utils import attributes_to_dict, strip_diacritics, apply
from ArabicTools.validators import AttributesValidator
from ArabicTools.models import SpecialSet
from django.db.models import Model, ForeignKey, TextField, CharField


class Spellable(Model):
    class Meta:
        abstract = True
    spelling = CharField(max_length=MAX_SPELLING_LENGTH, validators=[])

    def get_without_diacritics(self):
        return strip_diacritics(self.spelling)

    def __str__(self):
        return self.spelling


class AttributesMixin(Model):
    class Meta:
        abstract = True
    attributes = TextField(validators=[AttributesValidator()])

    def get_attributes(self):
        return attributes_to_dict(self.attributes)


class AbstractPattern(Model):
    class Meta:
        abstract = True
    origin_form = CharField(max_length=255, default=DEFAULT_ROOT_SPELLING)
    result_form = CharField(max_length=255)
    origin_model = None
    result_model = None
    special_set = ForeignKey(SpecialSet)

    def get_result_model(self):
        if not self.result_model:
            raise NotImplementedError('must define "get_result_model" or "result_model"')
        return self.result_model

    def generate_spelling(self, origin_spelling):
        return apply(
            origin_form=self.origin_form,
            specials=self.special_set.get_specials(),
            word=origin_spelling,
            result_form=self.result_form
        )

    def apply(self, origin, save=False, *args, **kwargs):
        if self.get_result_model().objects.filter(parent=origin, pattern=self):
            raise ValueError('%s %s has already applied to %s %s' % (self._meta.verbose_name, self, origin._meta.verbose_name, origin))
        result = self.get_result_model()(spelling=self.generate_spelling(origin.spelling), parent=origin, pattern=self, *args, **kwargs)
        if save:
            result.save()
        return result

    def get_origin_form(self):
        if self.origin_pattern:
            return self.origin_pattern.get_result_form()

    def get_result_form(self):
        if self.get_origin_form():
            return self.generate_spelling(self.get_origin_form())
        else:
            return ''

    def __str__(self):
        return self.get_result_form()
