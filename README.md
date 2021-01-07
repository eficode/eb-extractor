# Eventbrite extractor

Small script to extract list of participants for Eficode courses with
internal participants, based on the email address (``eficode.*``) which is
hardcoded.

Eventbrite documents their REST API at
https://www.eventbrite.com/platform/api#/reference/event

Note that the API has a limit of 1000 calls per hour.  The page size for each
of the items is 50.

The script can be invoked with

    ./getevents.py --output <file> --token <> --organization <id> --year [2020]

The token and organization id can be found in the web interface.  If the year
argument is not given, it defaults to 2020, which means that all events
with a start date in 2020 will be included.

The output file is a CSV file with the format::

    event name;start date;end date;name;email

Python 3.6+ is required to run this script.
