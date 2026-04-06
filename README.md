

*** senaite.batch.invoices


This function makes it possible for the lab to compile an invoice to the client for a LIMS Batch, keep it current and up to date, email it to the Client and save it to the Client's Invoices folder

Features
--------

This feature is enabled by checking the box for Batch Invoices  on the Financials tab in the LIMS setup

Batches have an Invoices tab where the cost of the analysis required for the Batch's Samples are reflected, one Sample per Invoice Line, and totalled at the bottom. All on an formal lab letterhead and Invoice format

Price per Sample includes both that of the Profiles as well as individual Analysis Services not in Profiles. The Invoice line description, is a concatenation of the price items used, Profile and Analysis Service titles

The Invoice is available throughout the Batch's life and can be issued before any work is done in the lab - some labs prefer to be paid upfront. If Analyses are added or removed from Samples, the prices are updated. Everytime the Invoice is issued it gets a unique sequence number based on the Batch ID

Invoices are issued by clicking the [Invoice] button on the Batch's Invoice tab. The system brings up a preview and the option to email the Invoice. Clicking through, an email template is displayed that can be edited before the Invoice is sent

The Invoice is saved to the Client’s Invoices folder where it can be looked up by both the lab and Client

Documentation
-------------
The Batch Invoice feature is discussed in more detail on the manual page https://www.bikalims.org/new-manual/billing-invoices

Installation
------------

Install senaite.batch.invoices by adding it to your buildout::

    [buildout]

    ...

    eggs =
        senaite.batch.invoices


and then running ``bin/buildout``


Contribute
----------
Issue Tracker: https://bika.atlassian.net/jira/dashboards/10000

Support
-------

Please post questions to the Bika Slack channels, request access at info@bikalims.org

The project is licensed under the GPLv2 by the Bika Open Source Collective, https://www.bikalims.org/

Copyright (C) 2019 Bika Lab Systems https://www.bikalabs.com/


