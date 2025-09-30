from rest_framework.test import APITestCase


class ApiEndpointsTests(APITestCase):
    def test_chat_and_recommend(self):
        # chat
        url_chat = "/api/chat"
        payload = {"session_id": "t1", "message": "I have a mild fever"}
        r = self.client.post(url_chat, payload, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("reply", r.data)
        self.assertIn("safety", r.data)

        # recommend
        url_rec = "/api/recommend"
        payload2 = {"session_id": "t1", "question": "What to do for mild fever in adult?", "top_k": 2}
        r2 = self.client.post(url_rec, payload2, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("answer", r2.data)
        self.assertIn("citations", r2.data)

        # upload report
        url_rep = "/api/upload_report"
        payload3 = {"session_id": "t1", "report_text": "Impression: normal. Recommendation: rest and hydration."}
        r3 = self.client.post(url_rep, payload3, format="json")
        self.assertEqual(r3.status_code, 200)
        self.assertIn("refined_report", r3.data)

        # get recommendation
        url_gr = "/api/get_recommendation"
        payload4 = {"session_id": "t1"}
        r4 = self.client.post(url_gr, payload4, format="json")
        self.assertEqual(r4.status_code, 200)
        self.assertIn("recommendation", r4.data)
        self.assertIn("session_notes_location", r4.data)
