import csv
from models import Asset
from datetime import datetime

Class
def get_exact_location(value):
    colon_split = value.split(':')
    if len(colon_split) > 1:
        return colon_split[1].lstrip()
    return ''


def parse_location(value):
    if value == 'None' or value == '' or value is None:
        return 'none'

    space_split = value.split(' ')
    first = space_split[0]

    if first == 'CCGS':
        second = space_split[1]
        last = space_split[-2]
        if last == '(Preparatory':
            return 'prep'
        elif second == 'Kooringal':
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

# TODO Find out how to run this from the command line!!

def import_assets():
    with open('../../asset_test_chunk_good.csv', 'rb') as f:
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

            asset = Asset(name=row[1],
                          manufacturer=row[2],
                          model=row[3],
                          serial=row[4],
                          location=location,
                          exact_location=exact_location,
                          owner=row[7],
                          purchase_date=datetime.strptime(row[10], '%d/%m/%Y'),
                          invoices=row[11],
                          wired_mac=row[8],
                          wireless_mac=row[9],
                          bluetooth_mac=row[10],
                          far_asset=row[12],
                          far_cost=row[13],
                          ed_cost=row[14],
                          warranty_period=row[15],
                          active=row[16])
            asset.save()

        # print '%s \t %s' % (location, exact_location)










#            _, created = Asset.objects.get_or_create(
#                First_Name=row[0],
#                Last_Name=row[1],
#                Middle_Name=row[2],
#                )
            # creates a tuple of the new object or
            # current object and a boolean of if it was created