.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://travis-ci.org/collective/senaite.batch.invoices.svg?branch=master
    :target: https://travis-ci.org/collective/senaite.batch.invoices

.. image:: https://coveralls.io/repos/github/collective/senaite.batch.invoices/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/senaite.batch.invoices?branch=master
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/v/senaite.batch.invoices.svg
    :target: https://pypi.python.org/pypi/senaite.batch.invoices/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/senaite.batch.invoices.svg
    :target: https://pypi.python.org/pypi/senaite.batch.invoices
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/senaite.batch.invoices.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/senaite.batch.invoices.svg
    :target: https://pypi.python.org/pypi/senaite.batch.invoices/
    :alt: License


======================
senaite.batch.invoices
======================

This function makes it possible for the lab to compile an invoice to the client for a LIMS Batch, keep it current and up to date, email it to the Client and save it to the Client's Invoices folder

Features
--------

This feature is enabled by checking the box for Batch Invoices  on the Financials tab in the LIMS setup

Batches have an Invoices tab where the cost of the analysis required for the Batch's Samples are reflected, one Sample per Invoice Line, and totalled at the bottom. All on an formal lab letterhead and Invoice format

Price per Sample includes both that of the Profiles as well as individual Analysis Services not in Profiles. The Invoice line description, is a concatenation of the price items used, Profile and Analysis Service titles

The Invoice is available throughout the Batch's life and can be issued before any work is done in the lab - some labs prefer to be paid upfront. If Analyses are added or removed from Samples, the prices are updated. Everytime the Invoice is issued it gets a unique sequence number based on the Batch ID

Invoices are issued by clicking the [Invoice] button on the Batch's Invoice tab. The system brings up a preview and the option to email the Invoice. Clicking through, an email template is displayed that can be edited before the Invoice is sent

The Invoice is saved to the Client’s Invoices folder where it can be looked up by both the lab and Client

Examples
--------

This add-on can be seen in action at the following sites:
- Is there a page on the internet where everybody can see the features?


Documentation
-------------

The Batch Invoice feature is discussed in more detail on the manual page https://www.bikalims.org/manual/17-billing



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

Issue Tracker: https://jira.bikalabs.com/

Documentation: https://www.bikalims.org/manual/17-billing


Support
-------

Please post questions to the Bika Slack channels, request access at info@bikalims.org

User group https://users.bikalims.org/

The project is licensed under the GPLv2 and sponsored by Geoangol, https://www.geoangol.site/ member of the Bika Open Source Collective, https://www.bikalims.org/

Copyright (C) 2019 Bika Lab Systems https://www.bikalabs.com/


