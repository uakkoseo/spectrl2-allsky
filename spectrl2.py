import pvlib as pvl
import pandas as pd
import glob


def this_site_info(loc, site_info):
    this_site_info = site_info.loc[loc]
    site = pvl.location.Location(
             latitude=this_site_info['Latitude'],
             longitude=this_site_info['Longitude'],
             tz=this_site_info['local_tz'],
             altitude=this_site_info['Elevation']
        )
    return site


def site_arguments(spectral_path, loc, dtadir):
    '''
    Function to create arguments based on weather data
    '''
    solcast_tmy = glob.glob(
        pathname='*.csv', root_dir= spectral_path / loc / 'Resource/Solcast'
        )[0]
    tmy_data_path = spectral_path / loc / 'Resource/Solcast' / solcast_tmy
    tmy = pd.read_csv(tmy_data_path, index_col=0, parse_dates=True)
    tmy_pressure = tmy['surface_pressure']*100
    # converting solcast pwat units to cm
    tmy_pwat = tmy['precipitable_water']/997*100
    tmy_zenith = tmy['zenith']
    tmy_times = tmy.index

    return tmy, tmy_pressure, tmy_pwat, tmy_zenith, tmy_times


def spectral2_arguments(tmy, tmy_solpos, tracker_config):
    tracker_angles = pvl.tracking.singleaxis(
        tmy_solpos.apparent_zenith,
        tmy.azimuth,
        tracker_config['axis_tilt'],
        tracker_config['axis_azimuth'],
        tracker_config['max_tracker_angle'],
        tracker_config['backtrack'],
        tracker_config['module_length']/tracker_config['pitch'])
    tmy_tilt = tracker_angles.tracker_theta
    tmy_aoi = tracker_angles.aoi
    tmy_relhum = pvl.atmosphere.get_relative_airmass(
         tmy_solpos.apparent_zenith, model='kastenyoung1989'
                                                   )

    return tracker_angles, tmy_tilt, tmy_aoi, tmy_relhum
