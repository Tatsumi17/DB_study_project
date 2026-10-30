import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from server import Handler

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_token = os.environ.get('SALES_API_TOKEN')
        os.environ['SALES_API_TOKEN'] = 'test-only'
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        if cls.old_token is None:
            os.environ.pop('SALES_API_TOKEN', None)
        else:
            os.environ['SALES_API_TOKEN'] = cls.old_token

    def request(self, path, auth=True, timeout=2):
        headers = {'Authorization': 'Bearer test-only'} if auth else {}
        try:
            response = urlopen(Request(self.base + path, headers=headers), timeout=timeout)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, response.read()

    def test_health_and_auth(self):
        self.assertEqual(self.request('/health', False)[0], 200)
        self.assertEqual(self.request('/v1/orders', False)[0], 401)
        self.assertEqual(self.request('/missing')[0], 404)

    def test_pagination_no_loss(self):
        ids = []
        for page in range(1, 4):
            status, _, body = self.request('/v1/orders?page=' + str(page))
            self.assertEqual(status, 200)
            result = json.loads(body)
            ids += [r['order_id'] for r in result['data']]
            self.assertEqual(result['meta']['next_page'], page + 1 if page < 3 else None)
        self.assertEqual(ids, ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'])
        self.assertEqual(json.loads(self.request('/v1/orders?page=10')[2])['data'], [])

    def test_same_name_different_identity(self):
        data = json.loads(self.request('/v1/customers?per_page=100')[2])['data']
        self.assertEqual(data[0]['name'], data[2]['name'])
        self.assertNotEqual(data[0]['customer_id'], data[2]['customer_id'])

    def test_correction_and_cancellation(self):
        a = json.loads(self.request('/v1/orders?revision=1')[2])
        b = json.loads(self.request('/v1/orders?revision=2')[2])
        self.assertEqual(a['data'][0]['amount'], 10000)
        self.assertEqual(b['data'][0]['amount'], 12000)
        self.assertEqual(b['data'][1]['status'], 'cancelled')
        self.assertNotEqual(a['meta']['snapshot_at'], b['meta']['snapshot_at'])

    def test_failure_modes(self):
        self.assertEqual(self.request('/v1/orders?mode=server_error')[0], 503)
        status, headers, _ = self.request('/v1/orders?mode=rate_limit')
        self.assertEqual(status, 429)
        self.assertEqual(headers['Retry-After'], '2')
        self.assertEqual(self.request('/v1/orders?fail_page=2&page=1')[0], 200)
        self.assertEqual(self.request('/v1/orders?fail_page=2&page=2')[0], 503)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(self.request('/v1/orders?mode=invalid_json')[2])
        malformed = json.loads(self.request('/v1/orders?mode=invalid_schema')[2])
        self.assertNotIn('meta', malformed)
        self.assertNotIsInstance(malformed['data'][0]['amount'], int)
        with self.assertRaises(TimeoutError):
            self.request('/v1/orders?mode=timeout', timeout=0.1)

    def test_invalid_query(self):
        for query in ['page=0', 'page=x', 'page=1&page=2', 'per_page=101', 'revision=3', 'mode=wrong', 'unknown=x', 'fail_page=-1']:
            with self.subTest(query=query):
                self.assertEqual(self.request('/v1/orders?' + query)[0], 400)

if __name__ == '__main__':
    unittest.main()
