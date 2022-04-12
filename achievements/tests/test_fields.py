from achievements.fields import CustomImageField


def test_field(filename_transliterations):
    custom_image_field_instance = CustomImageField(upload_to='media')
    assert callable(custom_image_field_instance.upload_to)
    for filename_transliteration in filename_transliterations:
        assert custom_image_field_instance.upload_to(None, filename_transliteration.initial_value) == (
            filename_transliteration.transliterated_value
        )
