#!/usr/bin/env python

import requests
import json
import datetime
import urllib3

class Controller():

    session = None
    endTime = "now-1s"

    def __init__(self, host, user, password, validate_certs=False):
        self.api = "https://" + host + "/api/v1"
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.session.verify = validate_certs
        self.headers = {"Content-Type": "application/json"}
        if ( validate_certs == False ):
            urllib3.disable_warnings()

    def do_post(self, uri, data, reauth=True):
        r = self.session.post(uri, data=data, headers=self.headers)
        if (r.status_code == 401 and reauth):
            self.login
            r = self.session.post(uri, data=data, headers=self.headers)
        return r

    def do_get(self, uri, reauth=True):
        r = self.session.get(uri)
        if (r.status_code == 401 and reauth):
            self.login
            r = self.session.get(uri)
        return r

    def login(self):
        uri = self.api + "/platform/login"
        data = json.dumps({"credentials":{'type': 'BASIC', 'username': self.user, 'password': self.password }})
        r = self.do_post(uri, data)
        #print("Login Result: {}\n{}\n".format(r.status_code, r.text))
        if (r.status_code == 204):
            return True
        else:
            return False

    def _get_events(self, uri, filter):
        if ( filter != None ):
            uri += "&filter={}".format(filter)
        r = self.do_get(uri)
        results = json.loads(r.text)
        if ( 'items' not in results ):
            results['items'] = [{"action_outcome":"fail","action_type":"event-collector","category":"audit_event", \
                    "level":"CRITICAL", "message":"Failed to get Events: {}".format(r.text), \
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z", "id": "deadbeef-dead-beef-dead-999999999999" }]
        return results

    # Returns events for the specified period, upto self.endTime.
    def get_events(self, period="1h", size=0, filter=None):
        uri = self.api + "/analytics/events?startTime=now-{}&endTime={}&pageSize={}".format(period, self.endTime, size)
        return self._get_events(uri, filter)

    # Returns events since the start (time or uuid), upto self.endTime.
    def get_events_since(self, start, size=0, filter=None):
        uri = self.api + "/analytics/events?startTime={}&endTime={}&pageSize={}".format(start, self.endTime, size)
        events = self._get_events(uri, filter)
        return events

