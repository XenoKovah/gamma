from collections import namedtuple

from pytest import fixture

FileNameTransformation = namedtuple('FileNameTransformation', ['initial_value', 'transliterated_value'])


@fixture(scope='session')
def filename_transliterations():
    return [
        FileNameTransformation('files/non-numeric    byte-string.png', 'media/files/non-numeric_byte-string.png'),
        FileNameTransformation(
            'blob/Снимок экрана 2022-04-12 в 09.49.29.jpeg',
            'media/blob/snimok_ekrana_2022-04-12_v_09.49.29.jpeg'
        ),
    ]
