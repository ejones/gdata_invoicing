gdata_invoicing
===============

This is how I create my invoices. I wrote it for an Ontario (Canada) Corporation, but it could be pretty easily tailored for another jurisdiction.

This module generates an invoice as a PDF from your Google Calendar. It just takes all entries ("events") on the calendar and assumes that they're billable hours, so it really just makes sense to create a separate calendar for each client and use that. I don't bother giving these events a name; currently the script does not do anything with the event name (but it could be customized to use it as the line-item description, say).

To generate the invoices, you create a Python script and call the ``gdata_invoicing.main`` function with the desired parameters as kwargs. So if your email was "foo.bar@gmail.com" and the calendar in question was "some-client", it might look like this::

    from gdata_invoicing import main, obj
    from getpass import getpass

    main(
        title='Invoice',
        number='2011-000',
        invoicer=obj( name="My Company Inc.",
                      address="123 Anywhere St.\nMiddleville ON A1A 1A1" ),
        user='foo.bar@gmail.com',
        password=getpass(),
        calendar='some-client'
        # ...
    )

See ``template.py`` in the project root for a *non-functional* but complete template.

Copyright (C) 2011 by Evan Jones. Licensed under MIT.
