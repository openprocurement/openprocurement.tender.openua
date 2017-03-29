# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest, test_bids
)


# TenderCancellationResourceTest


def create_tender_cancellation_invalid(self):
    response = self.app.post_json('/tenders/some_id/cancellations', {
        'data': {'reason': 'cancellation reason'}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
    ])

    request_path = '/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header',
         u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'No JSON object could be decoded',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(
        request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'reason'},
    ])

    response = self.app.post_json(request_path, {'data': {
        'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': {
                                      'reason': 'cancellation reason',
                                      "cancellationOf": "lot"
                                  }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedLot'}
    ])

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                  {'data': {
                                      'reason': 'cancellation reason',
                                      "cancellationOf": "lot",
                                      "relatedLot": '0' * 32
                                  }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedLot should be one of lots'], u'location': u'body', u'name': u'relatedLot'}
    ])


def create_tender_cancellation(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertIn('date', cancellation)
    self.assertEqual(cancellation['reasonType'], 'cancelled')
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'active.tendering')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token),
        {'data': {'reason': 'cancellation reason', 'status': 'active', 'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reasonType'], 'unsuccessful')
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'cancelled')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't add cancellation in current (cancelled) tender status")


def patch_tender_cancellation(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    old_date_status = response.json['data']['date']
    response = self.app.patch_json(
        '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token),
        {"data": {'reasonType': 'unsuccessful'}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["reasonType"], "unsuccessful")

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertNotEqual(old_date_status, response.json['data']['date'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], 'cancelled')

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update cancellation in current (cancelled) tender status")

    response = self.app.patch_json('/tenders/{}/cancellations/some_id?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'cancellation_id'}
    ])

    response = self.app.patch_json('/tenders/some_id/cancellations/some_id', {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["reason"], "cancellation reason")


def get_tender_cancellation(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']

    response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], cancellation)

    response = self.app.get('/tenders/{}/cancellations/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'cancellation_id'}
    ])

    response = self.app.get('/tenders/some_id/cancellations/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def get_tender_cancellations(self):
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']

    response = self.app.get('/tenders/{}/cancellations'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][0], cancellation)

    response = self.app.get('/tenders/some_id/cancellations', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


# TenderLotCancellationResourceTest


def create_tender_lot_cancellation(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
    self.assertEqual(response.json['data']["status"], 'active.tendering')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
    self.assertEqual(response.json['data']["status"], 'cancelled')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation in current (cancelled) tender status")


def patch_tender_lot_cancellation(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
    self.assertEqual(response.json['data']["status"], 'cancelled')

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

    response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["reason"], "cancellation reason")


# TenderLotsCancellationResourceTest


def create_tender_lots_cancellation(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
    self.assertEqual(response.json['data']["status"], 'active.tendering')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
    self.assertNotEqual(response.json['data']["status"], 'cancelled')

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")


def patch_tender_lots_cancellation(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        "cancellationOf": "lot",
        "relatedLot": lot_id
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
    self.assertNotEqual(response.json['data']["status"], 'cancelled')

    response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
        self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

    response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["status"], "active")
    self.assertEqual(response.json['data']["reason"], "cancellation reason")


# TenderAwardsCancellationResourceTest


def cancellation_active_award(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    for i in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, i['id']),
                                      {'data': {'bids': auction_bids_data}})

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                   {"data": {"status": "active", "qualified": True, "eligible": True}})

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])


def cancellation_unsuccessful_award(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    auction_bids_data = response.json['data']['bids']
    for i in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, i['id']),
                                      {'data': {'bids': auction_bids_data}})

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                   {"data": {"status": "unsuccessful"}})

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == self.initial_lots[0]['id']][0]
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                                   {"data": {"status": "unsuccessful"}})

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all awards is unsuccessful")

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation if all awards is unsuccessful")

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    cancellation = response.json['data']
    self.assertEqual(cancellation['reason'], 'cancellation reason')
    self.assertEqual(cancellation['status'], 'active')
    self.assertIn('id', cancellation)
    self.assertIn(cancellation['id'], response.headers['Location'])


# TenderCancellationDocumentResourceTest


def not_found(self):
    response = self.app.post('/tenders/some_id/cancellations/some_id/documents', status=404, upload_files=[
                             ('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.post('/tenders/{}/cancellations/some_id/documents?acc_token={}'.format(
        self.tender_id, self.tender_token), status=404, upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'cancellation_id'}
    ])

    response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, self.cancellation_id, self.tender_token), status=404, upload_files=[
                             ('invalid_value', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.get('/tenders/some_id/cancellations/some_id/documents', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'cancellation_id'}
    ])

    response = self.app.get('/tenders/some_id/cancellations/some_id/documents/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'cancellation_id'}
    ])

    response = self.app.get('/tenders/{}/cancellations/{}/documents/some_id'.format(self.tender_id, self.cancellation_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'document_id'}
    ])

    response = self.app.put('/tenders/some_id/cancellations/some_id/documents/some_id', status=404,
                            upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.put('/tenders/{}/cancellations/some_id/documents/some_id?acc_token={}'.format(
        self.tender_id, self.tender_token), status=404, upload_files=[('file', 'name.doc', 'content2')])

    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'cancellation_id'}
    ])

    response = self.app.put('/tenders/{}/cancellations/{}/documents/some_id?acc_token={}'.format(
        self.tender_id, self.cancellation_id, self.tender_token), status=404, upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
    ])


def create_tender_cancellation_document(self):
    response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
        self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/cancellations/{}/documents'.format(self.tender_id, self.cancellation_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/cancellations/{}/documents?all=true'.format(self.tender_id, self.cancellation_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?download=some_id'.format(
        self.tender_id, self.cancellation_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
        self.tender_id, self.cancellation_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
        self.tender_id, self.cancellation_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('complete')

    response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
        self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")


def put_tender_cancellation_document(self):
    response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
        self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.cancellation_id, doc_id, self.tender_token),
                            status=404, upload_files=[('invalid_name', 'name.doc', 'content')])

    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
        self.tender_id, self.cancellation_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
        self.tender_id, self.cancellation_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.cancellation_id, doc_id, self.tender_token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
        self.tender_id, self.cancellation_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    self.set_status('complete')

    response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


def patch_tender_cancellation_document(self):
    response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
        self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.cancellation_id, doc_id, self.tender_token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
        self.tender_id, self.cancellation_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    self.set_status('complete')

    response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.cancellation_id, doc_id, self.tender_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")
