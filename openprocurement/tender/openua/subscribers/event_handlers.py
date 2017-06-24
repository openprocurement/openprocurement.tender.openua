# -*- coding: utf-8 -*-
from pyramid.events import subscriber
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.api.utils import get_now, calculate_business_date

from openprocurement.tender.openua.models import EnquiryPeriod, \
    ENQUIRY_PERIOD_TIME, ENQUIRY_STAND_STILL_TIME


@subscriber(TenderInitializeEvent, procurementMethodType="openua")
def tender_init_handler(event):
    """ initialization handler for openua tenders """
    tender = event.tender
    endDate = calculate_business_date(tender.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, tender)
    tender.enquiryPeriod \
        = EnquiryPeriod(dict(startDate=tender.tenderPeriod.startDate,
                             endDate=endDate,
                             invalidationDate=tender.enquiryPeriod and tender.enquiryPeriod.invalidationDate,
                             clarificationsUntil=calculate_business_date(endDate,
                                                                         ENQUIRY_STAND_STILL_TIME, tender,
                                                                         True)))
    now = get_now()
    tender.date = now
    if tender.lots:
        for lot in tender.lots:
            lot.date = now
