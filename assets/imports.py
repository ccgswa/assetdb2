import csv
import os
from django.contrib.auth.models import User
from models import Asset, AssetHistory
from datetime import datetime


def parse_date(value):
    if value != '':
        return datetime.strptime(value, '%Y-%m-%d').date()
    return None


def parse_datetime(value):
    if value != '':
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return None


def parse_location_id(location_id, location_dict):
    """
    Parses location id values from the old database to be compatible with the new asset model without anh data loss.

    :param      location_id: ID corresponding to an entry in the locations_location table of the original asset database

    :param      location_dict: A dictionary of locations_location information with
                key: 'id' and value: ('name', 'description')

    :return:    (location, exact_location) filtered to fit into the new database.

                IMPORTANT: exact_location must be prepended to any pre-existing entries in the old database.
    """

    location = ''
    exact_location = ''

    if location_id == '':

        location = 'none'

    else:
        location_id = int(location_id)
        if location_id in (2, 46, 47, 60, 62, 83):  # If anything other than a ccgs location
            if location_id in (2, 46, 62):
                location = 'disposed'
                if location_id == 2:  # Offsite
                    exact_location = location_dict.get(str(location_id))[0]
                elif location_id == 62:  # Warranty return to manufacturer
                    exact_location = 'Warranty return to manufacturer'
            elif location_id == 83:
                location = 'damaged'
            elif location_id == 47:
                location = 'lost'
            elif location_id == 60:
                location = 'kooringal'

        else:  # Location will be 'ccgs'
            location = 'ccgs'

            if location_id != 1:  # If main campus don't prepend anything
                if location_id in (4, 23, 28, 45, 49, 56, 57, 63, 69, 70):  # If we're not using the existing 'name' field
                    if location_id == 4 or location_id == 28:  # Use description only
                        exact_location = location_dict.get(str(location_id))[1]
                    elif location_id == 23:
                        exact_location = 'L23: Open Studio'
                    elif location_id == 45:
                        exact_location = 'Block V: Comms Room'
                    elif location_id == 49:
                        exact_location = 'Block K: CLC Admin'
                    elif location_id == 56:
                        exact_location = 'Music Dept'
                    elif location_id == 57:
                        exact_location = 'Block K: CLC Library'
                    elif location_id == 63:
                        exact_location = 'Block Q'
                    elif location_id == 69:
                        exact_location = 'D1: Prep Staff Room'
                    elif location_id == 70:
                        exact_location = 'D2: Prep Library'
                else:
                    # Prepend name first
                    exact_location = location_dict.get(str(location_id))[0]
                    # Then additional information
                    if location_id == 3:
                        exact_location += ': ICT Centre and Gallery'
                    elif 6 <= location_id <= 20 or 51 <= location_id <= 55 or location_id in (25, 26, 44, 48, 59, 61, 64, 65, 66):
                        exact_location += ': %s' % location_dict.get(str(location_id))[1]

    return location, exact_location


def get_location_dict():
    """
    Generates a dictionary of {'id':('name', 'description')} from the old locations_location database table

    :return: A neat little dictionary for use in parsing location values.
    """
    os.chdir('/Users/gnolan/dev/python/assets_export/')
    location_csv = 'locations_location.csv'

    with open(location_csv, 'rb') as f:
        reader = csv.reader(f)

        reader.next()  # Skip the header row
        location_dict = {row[0]: tuple(row[1:3]) for row in reader}

    return location_dict


def print_locations():
    """
    Used to inspect the validity of parsed location data
    :return: No return value.
    """
    os.chdir('/Users/gnolan/dev/python/assets_export/')
    asset_csv = 'assets_asset.csv'

    location_dict = get_location_dict()

    with open(asset_csv, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            (loc, prepend) = parse_location_id(row[5], location_dict)
            exact_location = row[13]
            if prepend != '' and exact_location != '':
                exact_location = '%s - %s' % (prepend, exact_location)
            else:
                exact_location += prepend
            print (row[1], loc, exact_location)


def import_assets():
    """
        Let's get things done.
    """
    os.chdir('/Users/gnolan/dev/python/assets_export/')
    asset_csv = 'assets_asset.csv'

    location_dict = get_location_dict()

    with open(asset_csv, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            (location, prepend) = parse_location_id(row[5], location_dict)
            exact_location = row[13]
            if prepend != '' and exact_location != '':
                exact_location = '%s - %s' % (prepend, exact_location)
            else:
                exact_location += prepend
            # print (row[1], loc, exact_location)

            asset = Asset(id=row[0],
                          name=row[1],
                          manufacturer=row[2],
                          model=row[3],
                          serial=row[4],
                          location=location,
                          purchase_date=parse_date(row[6]),
                          warranty_period=row[7],
                          active=(row[8] == '1'),
                          owner=row[9],
                          wired_mac=row[10],
                          wireless_mac=row[11],
                          bluetooth_mac=row[12],
                          exact_location=exact_location,
                          far_asset=row[14],
                          far_cost=row[15],
                          ed_cost=row[16],
                          invoices=row[17],)
            asset.save()


def import_users():

    os.chdir('/Users/gnolan/dev/python/assets_export/')
    user_csv = 'auth_user.csv'

    with open(user_csv, 'rb') as f:
        reader = csv.reader(f)

        reader.next()  # Skip the header row
        for row in reader:
            user = User(id=row[0],
                        username=row[1],
                        first_name=row[2],
                        last_name=row[3],
                        email=row[4],
                        password=row[5],
                        is_staff=(row[6] == '1'),
                        is_active=(row[7] == '1'),
                        is_superuser=(row[8] == '1'),
                        last_login=parse_datetime(row[9]),
                        date_joined=parse_datetime(row[10]),)
            user.save()


def get_user_dict():
    """
    :return: Returns the correct id: username mappings for importing AssetHistory data.
    """
    os.chdir('/Users/gnolan/dev/python/assets_export/')
    user_csv = 'auth_user.csv'

    with open(user_csv, 'rb') as f:
        reader = csv.reader(f)

        reader.next()  # Skip the header row
        user_dict = {row[0]: row[1] for row in reader}

        for key, value in user_dict.iteritems():
            print key, value

    return user_dict


def import_history():

    os.chdir('/Users/gnolan/dev/python/assets_export/')
    history_csv = 'assets_assethistory.csv'
    user_dict = get_user_dict()
    transfer_dict = {'1': 'internal',
                     '2': 'outgoing',
                     '3': 'incoming'}

    with open(history_csv, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            username = user_dict.get(row[4])  # Get username of user from old database by id
            user_id = User.objects.get(username=username).user_id  # Map username to current database id

            ah = AssetHistory(id=row[0],
                              asset_id=row[1],
                              incident=row[2],
                              recipient=row[3],
                              created_by=user_id,
                              created_date=parse_datetime(row[5]),
                              transfer=transfer_dict.get(row[6]),
                              notes=row[7])
            ah.save()


def import_ip_addresses():

    os.chdir('/Users/gnolan/dev/python/assets_export/')
    ip_address_csv = 'assets_device.csv'

    return None



def get_exact_location(value):
    """
        DO NOT USE. Kept for reference purposes.
    """
    colon_split = value.split(':')
    if len(colon_split) > 1:
        return colon_split[1].lstrip()
    return ''


def parse_location(value):
    """
        DO NOT USE. Kept for reference purposes.
    """
    if value == 'None' or value == '' or value is None:
        return 'none'

    space_split = value.split(' ')
    first = space_split[0]

    if first == 'CCGS':
        second = space_split[1]
# Prep removed from asset model
#        last = space_split[-2]
#        if last == '(Preparatory':
#            return 'prep'
        if second == 'Kooringal':
            return 'kooringal'
        else:
            return 'ccgs'
    elif first == 'Damaged':
        return 'damaged'
    elif first == 'Disposed':
        return 'disposed'
    elif first == 'Stolen':
        return 'lost'

    return value


def legacy_import():

    """
    DO NOT USE. Kept for reference purposes.
    :return:
    """


#   import_dir = os.path.expanduser("~/dev/python/assets_export/")
    os.chdir('/Users/gnolan/dev/python/assets_export/')
    asset_csv = 'asset_test_chunk_good.csv'
    location_csv = 'locations_location.csv'

    with open(location_csv, 'rb') as f:
        reader = csv.reader(f)

        reader.next()


    with open(asset_csv, 'rb') as f:
        reader = csv.reader(f)

        # Skip the header line
        reader.next()
        # Import data
        for row in reader:

            location = parse_location(row[5])
            exact_location = row[6]

            if location not in ('ccgs', 'prep', 'kooringal', 'damaged', 'disposed', 'lost', 'none'):
                if exact_location == '':
                    exact_location = location
                else:
                    exact_location = '%s - %s' % (location, exact_location)
                location = 'none'

            elif location in ('ccgs', 'prep'):
                el = get_exact_location(row[5])
                if el != '':
                    if exact_location == '':
                        exact_location = el
                    else:
                        exact_location = '%s - %s' % (el, exact_location)

            # print '%s \t %s' % (location, exact_location)

            asset = Asset(id=row[0],
                          name=row[1],
                          manufacturer=row[2],
                          model=row[3],
                          serial=row[4],
                          location=location,
                          exact_location=exact_location,
                          owner=row[7],
                          purchase_date=parse_date(row[11]),
                          invoices=row[12],
                          wired_mac=row[8],
                          wireless_mac=row[9],
                          bluetooth_mac=row[10],
                          far_asset=row[13],
                          far_cost=row[14],
                          ed_cost=row[15],
                          warranty_period=row[16],
                          active=(row[17] == 'TRUE'))
            asset.save()


#            _, created = Asset.objects.get_or_create(
#                First_Name=row[0],
#                Last_Name=row[1],
#                Middle_Name=row[2],
#                )
            # creates a tuple of the new object or
            # current object and a boolean of if it was created