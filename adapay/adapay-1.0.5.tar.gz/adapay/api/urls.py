pay_message_token = '/v1/token/apply'

payment_create = '/v1/payments'
payment_query = '/v1/payments/{payment_id}'
payment_close = '/v1/payments/{}/close'

refund_create = '/v1/payments/{}/refunds'
refund_query = '/v1/payments/refunds'

bill_download = '/v1/bill/download'

member_create = '/v1/members'
member_query = '/v1/members/{member_id}'
member_query_list = '/v1/members/list'
member_update = '/v1/members/update'
corp_member_create = '/v1/corp_members'
corp_member_query = '/v1/corp_members/{member_id}'

settle_account_create = '/v1/settle_accounts'
settle_account_query = '/v1/settle_accounts/{settle_account_id}'
settle_account_delete = '/v1/settle_accounts/delete'
settle_account_detail_query = '/v1/settle_accounts/settle_details'
