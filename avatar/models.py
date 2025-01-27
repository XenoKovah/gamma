from django.db import models
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils.translation import ugettext_lazy as _

from avatar.constants import HEX_COLOR_REGEX
from users.models import GammaUser


class SkinType(models.Model):
    """
    Model representing different skin types for Avatar items (e.g., Glasses, Headdress, Outerwear).
    """

    name = models.CharField(max_length=255, verbose_name=_('Skin Type'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Skin Type')
        verbose_name_plural = _('Skin Types')


class AvatarColor(models.Model):
    """
    Model representing Avatar colors.
    """

    name = models.CharField(max_length=255, verbose_name=_('Color Name'))
    hex_color = models.CharField(
        max_length=7,
        verbose_name=_('Hex Color Code'),
        validators=[RegexValidator(HEX_COLOR_REGEX, _('Enter a valid hex color code'))]
    )

    def __str__(self):
        return f'{self.name} ({self.hex_color})'

    class Meta:
        verbose_name = _('Avatar Color')
        verbose_name_plural = _('Avatar Colors')


class AvatarBase(models.Model):
    """
    Model representing the base image for the User Avatar creation.
    """

    name = models.CharField(max_length=255, verbose_name=_('Base Name'))
    base_image = models.FileField(
        upload_to='static/images/avatar_bases/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Avatar Base')
        verbose_name_plural = _('Avatar Bases')


class UserAvatarConfig(models.Model):
    """
    Top-level model representing the User's Avatar configuration.
    """

    user = models.OneToOneField(GammaUser, on_delete=models.CASCADE)
    image = models.FileField(
        upload_to='static/images/user_avatars/',
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg', 'heic'])],
        null=True,
        blank=True
    )
    avatar_set = models.ForeignKey('AvatarSet', on_delete=models.SET_NULL, null=True)
    use_avatar = models.BooleanField(default=False, verbose_name=_('Use this avatar?'))

    def __str__(self):
        return f"{self.user.username}'s Avatar Config"

    class Meta:
        verbose_name = _('User Avatar Config')
        verbose_name_plural = _('User Avatar Configs')


class AvatarSet(models.Model):
    """
    Model representing a set of avatar items and attributes.
    """
    name = models.CharField(max_length=255, verbose_name=_('Set Name'))
    base_image = models.ForeignKey(AvatarBase, on_delete=models.SET_NULL, null=True, verbose_name=_('Base Image'))
    avatar_items = models.ManyToManyField('AvatarSetItem', blank=True, verbose_name=_('Avatar Items'))
    avatar_color = models.ForeignKey(AvatarColor, on_delete=models.SET_NULL, null=True, verbose_name=_('Avatar Color'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Avatar Set')
        verbose_name_plural = _('Avatar Sets')


class AvatarItem(models.Model):
    """
    Model representing individual avatar items (e.g., Glasses, Headdress, Outerwear).
    """

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    skin_type = models.ForeignKey(SkinType, on_delete=models.CASCADE)
    svg_file = models.FileField(
        upload_to='static/images/avatar_items/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.name} ({self.skin_type.name})'

    class Meta:
        verbose_name = _('Avatar Item')
        verbose_name_plural = _('Avatar Items')


class AvatarSetItem(models.Model):
    """
    Model representing the Avatar Item specified for definitive Avatar Set.
    """

    avatar_base = models.ForeignKey(AvatarBase, on_delete=models.CASCADE)
    avatar_item = models.ForeignKey(AvatarItem, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.avatar_item} for {self.avatar_base}'

    class Meta:
        verbose_name = _('Avatar Set Item')
        verbose_name_plural = _('Avatar Set Items')
        unique_together = (('avatar_base', 'avatar_item'),)
