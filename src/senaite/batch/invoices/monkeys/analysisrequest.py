# -*- coding: utf-8 -*-

import six
from collections import OrderedDict
from Products.CMFPlone.utils import safe_unicode
from zope.component import getAdapters
from zope.interface import alsoProvides

from bika.lims import api
from bika.lims.interfaces import IBatch
from bika.lims.workflow import doActionFor
from bika.lims.interfaces import IAddSampleRecordsValidator
from bika.lims.workflow import ActionHandlerPool

from senaite.batch.invoices import _
from senaite.batch.invoices import logger
from senaite.batch.invoices.utils.analysisrequest import \
    create_analysisrequest as crar


def ajax_submit(self):
    """Create samples and redirect to configured actions
    """
    # Check if there is the need to display a confirmation pane
    confirmation = self.check_confirmation()
    if confirmation:
        return {"confirmation": confirmation}

    # Get AR required fields (including extended fields)
    fields = self.get_ar_fields()

    # extract records from request
    records = self.get_records()

    fielderrors = {}
    errors = {"message": "", "fielderrors": {}}

    attachments = {}
    valid_records = []

    # Validate required fields
    for n, record in enumerate(records):

        # Process UID fields first and set their values to the linked field
        uid_fields = filter(lambda f: f.endswith("_uid"), record)
        for field in uid_fields:
            name = field.replace("_uid", "")
            value = record.get(field)
            if "," in value:
                value = value.split(",")
            record[name] = value

        # Extract file uploads (fields ending with _file)
        # These files will be added later as attachments
        file_fields = filter(lambda f: f.endswith("_file"), record)
        uploads = map(lambda f: record.pop(f), file_fields)
        attachments[n] = [self.to_attachment_record(f) for f in uploads]

        # Required fields and their values
        required_keys = [field.getName() for field in fields
                         if field.required]
        required_values = [record.get(key) for key in required_keys]
        required_fields = dict(zip(required_keys, required_values))

        # Client field is required but hidden in the AR Add form. We remove
        # it therefore from the list of required fields to let empty
        # columns pass the required check below.
        if record.get("Client", False):
            required_fields.pop('Client', None)

        # Check if analyses are required for sample registration
        if not self.analyses_required():
            required_fields.pop("Analyses", None)

        # Contacts get pre-filled out if only one contact exists.
        # We won't force those columns with only the Contact filled out to
        # be required.
        contact = required_fields.pop("Contact", None)

        # None of the required fields are filled, skip this record
        if not any(required_fields.values()):
            continue

        # Re-add the Contact
        required_fields["Contact"] = contact

        # Check if the contact belongs to the selected client
        contact_obj = api.get_object(contact, None)
        if not contact_obj:
            fielderrors["Contact"] = _("No valid contact")
        else:
            parent_uid = api.get_uid(api.get_parent(contact_obj))
            if parent_uid != record.get("Client"):
                msg = _("Contact does not belong to the selected client")
                fielderrors["Contact"] = msg

        # Missing required fields
        missing = [f for f in required_fields if not record.get(f, None)]

        # Handle fields from Service conditions
        for condition in record.get("ServiceConditions", []):
            if condition.get("type") == "file":
                # Add the file as an attachment
                file_upload = condition.get("value")
                att = self.to_attachment_record(file_upload)
                if att:
                    # Add the file as an attachment
                    att.update({
                        "Service": condition.get("uid"),
                        "Condition": condition.get("title"),
                    })
                    attachments[n].append(att)
                # Reset the condition value
                filename = file_upload and file_upload.filename or ""
                condition.value = filename

            if condition.get("required") == "on":
                if not condition.get("value"):
                    title = condition.get("title")
                    if title not in missing:
                        missing.append(title)

        # If there are required fields missing, flag an error
        for field in missing:
            fieldname = "{}-{}".format(field, n)
            msg = _("Field '{}' is required").format(safe_unicode(field))
            fielderrors[fieldname] = msg

        # Process valid record
        valid_record = dict()
        for fieldname, fieldvalue in six.iteritems(record):
            # clean empty
            if fieldvalue in ['', None]:
                continue
            valid_record[fieldname] = fieldvalue

        # append the valid record to the list of valid records
        valid_records.append(valid_record)

    # return immediately with an error response if some field checks failed
    if fielderrors:
        errors["fielderrors"] = fielderrors
        return {'errors': errors}

    # do a custom validation of records. For instance, we may want to rise
    # an error if a value set to a given field is not consistent with a
    # value set to another field
    validators = getAdapters((self.request, ), IAddSampleRecordsValidator)
    for name, validator in validators:
        validation_err = validator.validate(valid_records)
        if validation_err:
            # Not valid, return immediately with an error response
            return {"errors": validation_err}

    # Process Form
    actions = ActionHandlerPool.get_instance()
    actions.queue_pool()
    ARs = OrderedDict()
    for n, record in enumerate(valid_records):
        client_uid = record.get("Client")
        client = self.get_object_by_uid(client_uid)

        if not client:
            actions.resume()
            raise RuntimeError("No client found")

        # Create the Analysis Request
        try:
            ar = crar(
                client,
                self.request,
                record,
            )
        except Exception as e:
            actions.resume()
            errors["message"] = str(e)
            logger.error(e, exc_info=True)
            return {"errors": errors}

        # We keep the title to check if AR is newly created
        # and UID to print stickers
        ARs[ar.Title()] = ar.UID()

        # Create the attachments
        ar_attachments = filter(None, attachments.get(n, []))
        for attachment_record in ar_attachments:
            self.create_attachment(ar, attachment_record)

    actions.resume()

    batch_msg = transition_batch(self.context)
    level = "info"
    if len(ARs) == 0:
        message = _('No Samples could be created.')
        level = "error"
    elif len(ARs) > 1:
        message = _('Samples ${ARs} were successfully created. ${batch_msg}',
                    mapping={'ARs': safe_unicode(', '.join(ARs.keys())),
                             "batch_msg": batch_msg}
                    )
    else:
        message = _('Sample ${AR} was successfully created. ${batch_msg}',
                    mapping={'AR': safe_unicode(ARs.keys()[0]),
                             "batch_msg": batch_msg})

    # Display a portal message
    self.context.plone_utils.addPortalMessage(message, level)

    return self.handle_redirect(ARs.values(), message)


def transition_batch(context):
    setup = api.get_setup()
    schema = setup.Schema()
    financials = schema['Financials'].getAccessor(setup)()
    invfor = schema['InvoiceForPublishedSamplesOnly'].getAccessor(setup)()
    batch_msg = ''
    if financials and invfor:
        batch_msg = "Batch transitioned to To Be Invoiced."
        # transition batch
        # TODO: check for other conditions
        # alsoProvides(self.context, IBatch) not working
        if context.portal_type == 'Batch':
            batch = context
            success, message = doActionFor(batch, "to_be_invoiced")
    return batch_msg
