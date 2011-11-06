#! /usr/bin/env python
from getpass import getpass
from gdata_invoicing import main

main(
    title = 'Invoice',
    number = '2011-000',
    invoicer = dict( name = "My Company Inc.",
                     address = "1500 Anywhere St.,\nMiddleville ON A1A 1A1" ),
    invoicee = dict( name = 'Some Client',
                     address = '1502 Anywhere St.,\nMiddleville ON A1A 1A1' ),
    attention = 'Bob',
    gstNumber = '00000 0000',
    date = 'Nov 6, 2011',
    period = 'October 2011',
    businessNumber = '00000 0000',
    subject = 'Coming, seeing, conquering',

    rate = 00, # $/hr
    gstRate = .13, # this is now actually the HST rate

    filename = 'invoice.pdf',
    user = 'your.email@gmail.com',
    password = getpass(),
    calendar = 'some-client',
    range_min = '2011-10-01T00:00:00-04:00',
    range_max = '2011-10-31T23:59:59-04:00')
