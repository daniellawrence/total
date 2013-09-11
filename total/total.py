#!/usr/bin/env python
"""
total: a command line totaler to be it is a consumer of stdout.
Usually space or tab separated data, it will then offer the user magic variables
to do things like:

 $1     - The total of all the items in column 1
 $2:max - The maximum number in all of column 2
 $3:avg - The average number of the data in column 3
 $4:min - The minimum number in all of column 4

Example:
 $ vmstat 1 5 | total 'The average cache per second is $cache:avg'
 the average cache per second is 74880

TODO:
-----
* add stddev
* logic for hostinfo style value_report
"""
import sys
import re


def avg(data_set):
    """ Take a data set and turn it in to an average number for the dataset.
    """
    length = len(data_set)
    total = sum(data_set)
    return total / length


def all_numbers(data_set):
    """ work out if a data set is all numbers or not """
    for i in data_set:
        if not i.isdigit():
            return False
    return True


def only_numbers(data_set):
    """ Return a sub list of data_set, that only contains its numbers. """
    new_data_set = []
    for i in data_set:
        if not i:
            continue
        if '.' not in i and not i.isdigit():
            continue
        if '.' not in i:
            i = int(i)
        else:
            i = float(i)
        new_data_set.append(i)
    return new_data_set


def get_title(data_set):
    """ Check if the first item in the data_set is the title. """
    first_item = data_set[0]
    first_item = first_item.strip()
    first_item = first_item.lower()
    if not first_item:
        return None
    if not first_item.isdigit():
        return first_item.lower()
    return None


def process_data(delimiter=None, ignore=None):
    """ process stdin to work out min, max, avg, totals, counts. """

    stdin_lines = sys.__stdin__.readlines()

    if len(stdin_lines) == 0:
        print "No data was found in the stdin buffer"
        sys.exit(4)

    raw_data = []
    data = {}

    # metadata
    line_lengths = {}
    most_line_length = 0
    most_line_length_count = 0

    # capture all the data for later use
    for line in stdin_lines:
        # skip over any lines that match the ignore pattern.
        if ignore and re.match(ignore, line):
            continue

        bits = list(' ') + line.split(delimiter)
        raw_data.append(bits)

        line_len = len(bits)

        if line_len not in line_lengths:
            line_lengths[line_len] = 0

        line_lengths[line_len] += 1

    # find the line length that most of the lines conform to.
    for length, count in line_lengths.items():
        if count > most_line_length_count:
            most_line_length = length
            most_line_length_count = count

    for line in raw_data:

        if len(line) != most_line_length:
            continue

        for bit_no, bit in enumerate(line):

            if bit_no not in data:
                data[bit_no] = []

            try:
                str_bit = str(bit)
            except ValueError as error:
                print "Unable to convert '%s' to str()" % error
                continue

            data[bit_no].append(str_bit)

    # If we were not able to capture any data then don't try and process it.
    data_length = len(data)
    if data_length == 0:
        print "Unable to process data, you might want to change the delimiter"
        print "You can change the delimiter via the '-d' or '--delimiter' flag"
        sys.exit(1)

    # loop over the captured data, we make a copy of the data dict() as we
    # modify the data's length in the loop.
    for col, col_data in data.copy().items():

        title = get_title(col_data)

        if title:
            col_data = col_data[1:]
        if not title:
            title = str(col)

        # So far all these operations will work without making sure all the the
        # data is numbers.
        data['%s:count' % col] = len(col_data)
        data['%s:list' % col] = ",".join(data[col])
        #data['%s:most' % col] = ",".join( data[col] )

        data['%s:count' % title] = len(col_data)
        data['%s:list' % title] = ",".join(data[col])
        #data['%s:most' % title] = data[col]

        # allow for the logic of $key to really be $key_total
        data['%s' % col] = "%d (count)" % len(col_data)
        data['%s' % title] = "%d (count)" % len(col_data)

        # if the col_data is not all_numbers then set the col_data to be
        # only_numbers
        # if not all_numbers( col_data ):
        col_data = only_numbers(col_data)

        # count that shows only the numbers - NumberCOUNT
        data['%s:ncount' % col] = len(col_data)
        data['%s:ncount' % title] = len(col_data)

        # If there is no col_data then do not try and work out avg, min, etc
        if len(col_data) == 0:
            continue

        # work out avg, min, etc
        data['%d:total' % col] = sum(col_data)
        data['%d:avg' % col] = avg(col_data)
        data['%d:min' % col] = min(col_data)
        data['%d:max' % col] = max(col_data)

        data['%s:total' % title] = sum(col_data)
        data['%s:avg' % title] = avg(col_data)
        data['%s:min' % title] = min(col_data)
        data['%s:max' % title] = max(col_data)

        # allow for the logic of $key to really be $key:total
        data['%s' % col] = data["%s:total" % col]
        data['%s' % title] = data["%s:total" % col]

    return data


def col_list(data):

    print "You can use the following cols for: :total, :avg, :min, :max"
    cols = set([])
    all_keys = data.keys()
    num_col = set([])

    for key in all_keys:
        if type(key) == type(int()):
            continue
        if not key:
            continue
        if ':' not in key:
            continue
        key = key.split(':')[0]

        if key.isdigit():
            num_col.add(key)
            continue
        cols.add(key.split(':')[0])

    if cols:
        print ", ".join(sorted(cols))
    if not cols:
        print ", ".join(num_col)


def _main(user_display, delimiter=None, ignore=None, list_only=None):
    # process the data from stdin
    data = process_data(delimiter, ignore)

    if list_only:
        col_list(data)
        sys.exit(1)

    user_display = user_display.replace('%', '%%')

    # the format should have alteast 1: $key
    if '$' not in user_display:
        print 'Looks like you are missing a $key in your format'
        sys.exit(2)

    # replace all the $key with $(key)s.
    # This makes it easy for users to enter in a key.
    # And allowed python to do the dict() mapping to the string.
    converted_display = re.sub('(?P<m>\$\w+)', "\g<m>:total", user_display)
    converted_display = re.sub(
        '\$(?P<m>\w+:\w+)', "%(\g<m>)s", converted_display)

    # print "DEBUG: %s" % converted_display

    return_string = None
    try:
        return_string = converted_display % data
    except KeyError as error:
        print "Wasn't able to find data for the key %s" % error
        sys.exit(3)
        # print "Keys that where found: %s" % ", ".join( data.keys())

    print return_string


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('format', metavar='format', type=str, default='$1')

    # added cut style delimiter logic
    parser.add_argument('-d', '--delimiter', metavar='delimiter', type=str)

    # added grep style ignore logic
    parser.add_argument('-v', '--ignore', metavar='ignore', type=str)

    # added grep style ignore logic
    parser.add_argument(
        '--list', dest='list_only', action='store_const', const='True')

    # grab the args
    args = parser.parse_args()
    user_display = args.format
    delimiter = args.delimiter
    ignore = args.ignore
    list_only = args.list_only

    # call _main()
    _main(user_display, delimiter, ignore, list_only)

if __name__ == '__main__':
    main()
