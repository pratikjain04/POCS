import os
import pytest

from astropy.coordinates import EarthLocation
from astropy import units as u

from pocs.images import OffsetError
from pocs.mount.ioptron import Mount
from pocs.utils.config import load_config


@pytest.fixture
def location():
    config = load_config(ignore_local=True)
    loc = config['location']
    return EarthLocation(lon=loc['longitude'], lat=loc['latitude'], height=loc['elevation'])


@pytest.fixture(scope="function")
def mount(config, location):
    try:
        del os.environ['POCSTIME']
    except KeyError:
        pass

    config['mount'] = {
        'brand': 'bisque',
        'template_dir': 'resources/bisque',
    }
    return Mount(location=location, config=config)


@pytest.mark.with_mount
def test_loading_without_config():
    """ Tests the basic loading of a mount """
    with pytest.raises(TypeError):
        mount = Mount()
        assert isinstance(mount, Mount)


@pytest.mark.with_mount
class TestMount(object):

    """ Test the mount """

    @pytest.fixture(autouse=True)
    def setup(self, config):

        self.config = config

        location = self.config['location']

        with pytest.raises(AssertionError):
            mount = Mount(location)

        loc = EarthLocation(
            lon=location['longitude'],
            lat=location['latitude'],
            height=location['elevation'])

        mount = Mount(loc)
        assert mount is not None

        self.mount = mount

        with pytest.raises(AssertionError):
            assert self.mount.query('version') == 'V1.00'
        assert self.mount.is_initialized is False
        assert self.mount.initialize() is True

    def test_version(self):
        assert self.mount.query('version') == 'V1.00'

    def test_set_park_coords(self):
        self.mount.initialize()
        assert self.mount._park_coordinates is None

        self.mount.set_park_coordinates()
        assert self.mount._park_coordinates is not None

        # These are the empirically determined coordinates for PAN001
        assert self.mount._park_coordinates.dec.value == -10.0
        assert self.mount._park_coordinates.ra.value - 322.98 <= 1.0

    def test_unpark_park(self):
        assert self.mount.is_parked is True
        self.mount.initialize()
        self.mount.unpark()
        assert self.mount.is_parked is False
        self.mount.home_and_park()
        assert self.mount.is_parked is True


def test_get_tracking_correction(mount):

    offsets = [
        # HA, ΔRA, ΔDec, Magnitude
        (2, -13.0881456, 1.4009, 12.154),
        (2, -13.0881456, -1.4009, 12.154),
        (2, 13.0881456, 1.4009, 12.154),
        (14, -13.0881456, 1.4009, 12.154),
        (14, 13.0881456, 1.4009, 12.154),
    ]

    corrections = [
        (103.49, 'south', 966.84, 'east'),
        (103.49, 'north', 966.84, 'east'),
        (103.49, 'south', 966.84, 'west'),
        (103.49, 'north', 966.84, 'east'),
        (103.49, 'north', 966.84, 'west'),
    ]

    for offset, correction in zip(offsets, corrections):
        pointing_ha = offset[0]
        offset_info = OffsetError(
            offset[1] * u.arcsec,
            offset[2] * u.arcsec,
            offset[3] * u.arcsec
        )
        correction_info = mount.get_tracking_correction(offset_info, pointing_ha)

        dec_info = correction_info['dec']
        ra_info = correction_info['ra']

        assert dec_info[1] == pytest.approx(correction[0], rel=1e-2)
        assert dec_info[2] == correction[1]

        assert ra_info[1] == pytest.approx(correction[2], rel=1e-2)
        assert ra_info[2] == correction[3]
