from openprocurement.api.validation import validate_data, validate_json_data, OPERATIONS
from openprocurement.api.utils import apply_data_patch, error_handler, get_now, raise_operation_error
from openprocurement.tender.core.utils import calculate_business_date


def validate_patch_tender_ua_data(request):
    data = validate_json_data(request)
    # TODO try to use original code openprocurement.tender.core.validation.validate_patch_tender_data
    if request.context.status == 'draft':
        default_status = type(request.tender).fields['status'].default
        if data and data.get('status') != default_status:
            raise_operation_error(request, 'Can\'t update tender in current (draft) status')
        request.validated['data'] = {'status': default_status}
        request.context.status = default_status
        return
    if data:
        if 'items' in data:
            items = request.context.items
            cpv_group_lists = [i.classification.id[:3] for i in items]
            for item in data['items']:
                if 'classification' in item and 'id' in item['classification']:
                    cpv_group_lists.append(item['classification']['id'][:3])
            if len(set(cpv_group_lists)) != 1:
                request.errors.add('body', 'item', 'Can\'t change classification')
                request.errors.status = 403
                raise error_handler(request.errors)
        if 'enquiryPeriod' in data:
            if apply_data_patch(request.context.enquiryPeriod.serialize(), data['enquiryPeriod']):
                request.errors.add('body', 'item', 'Can\'t change enquiryPeriod')
                request.errors.status = 403
                raise error_handler(request.errors)

    return validate_data(request, type(request.tender), True, data)

# bids
def validate_update_bid_to_draft(request):
    bid_status_to = request.validated['data'].get("status", request.context.status)
    if request.context.status != 'draft' and bid_status_to == 'draft':
        request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_bid_to_active_status(request):
    bid_status_to = request.validated['data'].get("status", request.context.status)
    if bid_status_to != request.context.status and bid_status_to != 'active':
        request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
        request.errors.status = 403
        raise error_handler(request.errors)

# complaint
def validate_submit_claim_time(request):
    tender = request.context
    claim_submit_time = request.content_configurator.tender_claim_submit_time
    if get_now() > calculate_business_date(tender.tenderPeriod.endDate, -claim_submit_time, tender):
        raise_operation_error(request, 'Can submit claim not later than {0.days} days before tenderPeriod end'.format(claim_submit_time))

# complaint documents
def validate_complaint_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] not in ['active.tendering']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))

# contract
def validate_contract_update_with_accepted_complaint(request):
    tender = request.validated['tender']
    if any([any([c.status == 'accepted' for c in i.complaints]) for i in tender.awards if i.lotID in [a.lotID for a in tender.awards if a.id == request.context.awardID]]):
        raise_operation_error(request, 'Can\'t update contract with accepted complaint')

# cancellation
def validate_cancellation(request):
    tender = request.validated['tender']
    cancellation = request.validated['cancellation']
    if not cancellation.relatedLot and tender.lots:
        active_lots = [i.id for i in tender.lots if i.status == 'active']
        statuses = [set([i.status for i in tender.awards if i.lotID == lot_id]) for lot_id in active_lots]
        block_cancellation = any([not i.difference({'unsuccessful', 'cancelled'}) if i else False for i in statuses])
    elif cancellation.relatedLot and tender.lots or not cancellation.relatedLot and not tender.lots:
        statuses = set([i.status for i in tender.awards if i.lotID == cancellation.relatedLot])
        block_cancellation = not statuses.difference({'unsuccessful', 'cancelled'}) if statuses else False
    else:
        block_cancellation = False
    if block_cancellation:
        raise_operation_error(request, 'Can\'t {} cancellation if all awards is unsuccessful'.format(
            OPERATIONS.get(request.method)))
