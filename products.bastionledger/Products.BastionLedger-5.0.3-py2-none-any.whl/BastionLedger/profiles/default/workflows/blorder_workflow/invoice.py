##parameters=state_info
order = state_info.object
if order.status() == 'invoiced':
    order.manage_reinvoice()
else:
    order.manage_invoice()
