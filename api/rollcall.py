class TronClassRollCallAPI:
    def __init__(self, session):
        self.session = session

    def getRollCall(self):
        url = "https://iclass.tku.edu.tw/api/radar/rollcalls?api_version=1.1.0"
        self.session.get(url)
        response.raise_for_status()
                data = response.json()
                rollcall_id = ""
                rollcalls = data.get('rollcalls', [])
                for rollcall in rollcalls:
                    if rollcall.get('rollcall_id'):
                        print(f"Found rollcall: ID = {rollcall['rollcall_id']}, Source = {rollcall['source']}")
                        return rollcall['rollcall_id'],rollcall['source']

    def answer_rollcall_number(self,rollcall_id,number,deviceId):
        url = f"https://iclass.tku.edu.tw/api/rollcall/{rollcall_id}/answer_number_rollcall"

        headers = {
            "host": "iclass.tku.edu.tw",
            "sec-ch-ua-platform": "\"Android\"",
            "accept-language": "zh-Hant",
            "sec-ch-ua": "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Linux; Android 14; SM-A146P Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.111 Mobile Safari/537.36 TronClass/googleplay",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "http://localhost",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "http://localhost/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "priority": "u=1, i"
        }
        code = f"{number:04d}"
        data = {
            "deviceId": deviceId,
            "numberCode": code,
        }
        response = self.session.put(url,headers,data=data)
        return response

    def answer_rollcall_Radar(session, rollcall_id, deviceId):
        url = f"https://iclass.tku.edu.tw/api/rollcall/{rollcall_id}/answer?api_version=1.1.2"

        headers = {
            "sec-ch-ua-platform": "\"Android\"",
            "accept-language": "zh-Hant",
            "sec-ch-ua": "\"Android WebView\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": ("Mozilla/5.0 (Linux; Android 14; SM-A146P Build/UP1A.231005.007; wv) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.111 "
                        "Mobile Safari/537.36 TronClass/googleplay"),
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "http://localhost",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "http://localhost/"
        }

        payload = {
            "deviceId": deviceId, #7eba2081f77e5527
            "latitude": 25.174269373936202,
            "longitude": 121.45422774303604,
            "speed": None,
            "accuracy": 34.400001525878906,
            "altitude": 77.69999694824219,
            "altitudeAccuracy": None,
            "heading": None
        }

        response = session.put(url, headers=headers, data=json.dumps(payload))
        return response
