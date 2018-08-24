#!/usr/bin/env python
#
# Copyright 2018 TWTG B.V.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = "Marten Lootsma, Stefan Korenberg"
__copyright__ = "Copyright 2018, TWTG B.V."
__credits__ = ["Marten Lootsma", "Stefan Korenberg"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Marten Lootsma"
__email__ = "marten@twtg.io"
__status__ = "Development"

from datetime import datetime
import pytz, requests, hashlib
import argparse

def sha256(input_bytes):
    """Hashes input_bytes using SHA256."""
    return hashlib.sha256(input_bytes).hexdigest()


def get_token(query_params, lrc_as_key):
    """Construct a token for LoRa KPN according to their instructions.

    Instructions:
        https://drive.google.com/file/d/1YOLehIt0IzqpmwTkmHYRxEVhXmR97Dpm/view (1.3.2)
        LRC-AS Key = shared secret key.
    """
    hashed_bytes = query_params.encode('utf-8') + lrc_as_key
    return sha256(hashed_bytes)


def get_time_string():
    """Get a string containing the current time."""
    now = datetime.now(tz=pytz.utc)
    return now.isoformat()

def construct_url(dev_eui, fport, payload, as_id, time_str, lrc_as_key):
    """Construct url to send downlink message."""
    query_params = 'DevEUI={}&FPort={}&Payload={}&AS_ID={}&Time={}'.format(dev_eui, fport, payload, as_id, time_str)
    token = get_token(query_params, lrc_as_key)
    
    # 'url encode' timestring in url (after calculation of token)
    query_params = query_params.replace(":", "%3A")
    query_params = query_params.replace("+", "%2B")
    return 'https://api.kpn-lora.com/thingpark/lrc/rest/downlink?{}&Token={}'.format(query_params, token)

if __name__ == '__main__':
    example_time_str = '2016-01-11T14:28:00.333+02:00'
    example_url = 'https://api.kpn-lora.com/thingpark/lrc/rest/downlink?DevEUI=000000000F1D8693&FPort=1&Payload=00&AS_ID=app1.sample.com&Time=2016-01-11T14%3A28%3A00.333%2B02%3A00&Token=63a4ec6532937c9bcba109a75f731d6dc192c9df662dee56757634a8a6dc3f4c'
    
    parser = argparse.ArgumentParser(description='KPN LoRa Downlink generator')
    parser.add_argument('--compare', '-c', action='store_true', help='compare generated url with example')
    parser.add_argument('--dev_eui', '-d', type=str, nargs='?', default='000000000F1D8693',
                    help='device id as known by KPN in hex string')
    parser.add_argument('--fport', '-f', type=int, nargs='?', default=1,
                    help='the port to send to')
    parser.add_argument('--payload', '-p', type=str, nargs='?', default='00',
                    help='payload in hex string')
    parser.add_argument('--id', '-i', type=str, nargs='?', default='app1.sample.com',
                    help='the application id')
    parser.add_argument('--key', '-k', type=str, nargs='?', default='46ab678cd45df4a4e4b375eacd096acc',
                    help='the key as known by in hex string')
    args = parser.parse_args()

    if args.compare:
        time_str = example_time_str = '2016-01-11T14:28:00.333+02:00'
    else:
        time_str = get_time_string()
    
    url = construct_url(args.dev_eui, args.fport, args.payload, args.id, time_str, args.key)

    if args.compare:
        if url == example_url:
            print 'built url matches example'
        else:
            print 'built url does NOT match example'
            print 'example:  ', example_url
            print 'generated:', url 
    else:                
        print "Request:", url
        r = requests.post(url)
        print "Response:", r.text
