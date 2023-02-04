AddBatchInvoice = 'senaite.batch.invoices: Add BatchInvoice'

ADD_CONTENT_PERMISSIONS = {
    'BatchInvoice': AddBatchInvoice,
}


def setup_default_permissions(portal):
    mp = portal.manage_permission
    mp(AddBatchInvoice, ['Manager', 'LabManager', 'LabClerk'], True)


# Transition permissions
# ======================
TransitionInvoice = "senaite.batch.invoices: Transition: Invoice"
