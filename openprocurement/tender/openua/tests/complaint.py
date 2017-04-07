# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_lots, test_organization
)

from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest
)
from openprocurement.tender.belowthreshold.tests.complaint_blanks import (
    # TenderComplaintResourceTest
    create_tender_complaint_invalid,
    get_tender_complaint,
    get_tender_complaints,
    # TenderComplaintDocumentResourceTest
    not_found,
    create_tender_complaint_document,
)
from openprocurement.tender.openua.tests.complaint_blanks import (
    # TenderComplaintResourceTest
    create_tender_complaint,
    patch_tender_complaint,
    review_tender_complaint,
    # TenderComplaintDocumentResourceTest
    patch_tender_complaint_document,
    put_tender_complaint_document,
    # TenderLotAwardComplaintResourceTest
    create_tender_lot_award_complaint,
)


class TenderComplaintResourceTest(BaseTenderUAContentWebTest):
    author = test_organization
    test_create_tender_complaint_invalid = snitch(create_tender_complaint_invalid)
    test_create_tender_complaint = snitch(create_tender_complaint)
    test_patch_tender_complaint = snitch(patch_tender_complaint)
    test_review_tender_complaint = snitch(review_tender_complaint)
    test_get_tender_complaint = snitch(get_tender_complaint)
    test_get_tender_complaints = snitch(get_tender_complaints)


class TenderLotAwardComplaintResourceTest(BaseTenderUAContentWebTest):
    initial_lots = test_lots
    author = test_organization
    test_create_tender_lot_award_complaint = snitch(create_tender_lot_award_complaint)


class TenderComplaintDocumentResourceTest(BaseTenderUAContentWebTest):
    author = test_organization

    def setUp(self):
        super(TenderComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/tenders/{}/complaints'.format(
            self.tender_id),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    test_not_found = snitch(not_found)
    test_create_tender_complaint_document = snitch(create_tender_complaint_document)
    test_put_tender_complaint_document = snitch(put_tender_complaint_document)
    test_patch_tender_complaint_document = snitch(patch_tender_complaint_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
