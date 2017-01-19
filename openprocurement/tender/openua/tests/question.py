# -*- coding: utf-8 -*-
import unittest

from datetime import datetime, timedelta
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import test_lots, test_organization
from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_tender_data
from openprocurement.api.tests.question import BaseTenderQuestionResourceTest, BaseTenderLotQuestionResourceTest

class BaseTenderUAQuestionResourceTest(object):
    def test_create_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(
            self.tender_id), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']
        self.assertEqual(question['author']['name'], test_organization['name'])
        self.assertIn('id', question)
        self.assertIn(question['id'], response.headers['Location'])

        self.go_to_enquiryPeriod_end()
        response = self.app.post_json('/tenders/{}/questions'.format(
            self.tender_id), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

        self.set_status('active.auction')
        response = self.app.post_json('/tenders/{}/questions'.format(
            self.tender_id), {'data': {'title': 'question title', 'description': 'question description', 'author': test_organization}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add question only in enquiryPeriod")

class TenderUAQuestionResourceTest(BaseTenderUAContentWebTest, BaseTenderQuestionResourceTest, BaseTenderUAQuestionResourceTest):
    status = "active.auction"
    test_tender_data = test_tender_data

class TenderUALotQuestionResourceTest(BaseTenderUAContentWebTest, BaseTenderLotQuestionResourceTest):
    initial_lots = 2 * test_lots

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderUALotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
