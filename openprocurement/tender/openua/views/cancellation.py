# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation import TenderCancellationResource
from openprocurement.tender.core.validation import (
    validate_cancellation_data,
    validate_cancellation as validate_cancellation_base,
    validate_patch_cancellation_data
)
from openprocurement.tender.openua.utils import add_next_award
from openprocurement.tender.openua.validation import validate_cancellation


@optendersresource(name='aboveThresholdUA:Tender Cancellations',
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType='aboveThresholdUA',
                   description="Tender cancellations")
class TenderUaCancellationResource(TenderCancellationResource):

    def cancel_lot(self, cancellation=None):
        if not cancellation:
            cancellation = self.context
        tender = self.request.validated['tender']
        [setattr(i, 'status', 'cancelled') for i in tender.lots if i.id == cancellation.relatedLot]
        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(['cancelled']):
            self.cancel_tender()
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            tender.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            tender.status = 'complete'
        if tender.status == 'active.auction' and all([
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated['tender'].lots
            if i.status == 'active'
        ]):
            configurator = self.request.content_configurator
            add_next_award(self.request,
                           reverse=configurator.reverse_awarding_criteria,
                           awarding_criteria_key=configurator.awarding_criteria_key)

    @json_view(content_type="application/json",
               validators=(validate_cancellation_data, validate_cancellation_base, validate_cancellation),
               permission='edit_tender')
    def collection_post(self):
        return super(TenderUaCancellationResource, self).collection_post()

    @json_view(content_type="application/json",
               validators=(validate_patch_cancellation_data, validate_cancellation_base, validate_cancellation),
               permission='edit_tender')
    def patch(self):
        return super(TenderUaCancellationResource, self).patch()
