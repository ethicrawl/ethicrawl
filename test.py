from ethicrawl.client.http_request import HttpRequest
from ethicrawl.client.http_response import HttpResponse

import requests

# from ethicrawl import Ethicrawl

url = "https://www.google.com/"
url = "https://ichef.bbci.co.uk/ace/standard/976/cpsprodpb/eb2c/live/5726d750-fbf4-11ef-9e61-71ee71f26eb1.jpg"
http_request = HttpRequest(url=url)

response = requests.get(http_request.url, headers=http_request.headers)

http_response = HttpResponse(
    status_code=response.status_code,
    request=http_request,
    headers=response.headers,
    content=response.content,
    text=response.text,
)


print(http_response)

"""
HTTP 200
URL: https://ichef.bbci.co.uk/ace/standard/976/cpsprodpb/eb2c/live/5726d750-fbf4-11ef-9e61-71ee71f26eb1.jpg

Headers:
Server: AmazonS3
Last-Modified: Sun, 09 Mar 2025 00:10:24 GMT
ETag: "cbdb9089857819c9fca9f2ba9ac05a96"
x-amz-server-side-encryption: AES256
Accept-Ranges: bytes
Content-Type: image/jpeg
Content-Length: 135662
Expires: Mon, 09 Mar 2026 00:12:18 GMT
Cache-Control: max-age=31536000
Date: Thu, 13 Mar 2025 08:53:28 GMT
Connection: keep-alive
Timing-Allow-Origin: https://www.bbc.co.uk, https://www.bbc.com
Access-Control-Allow-Headers: *
Access-Control-Allow-Methods: HEAD,GET
Access-Control-Allow-Credentials: false
Access-Control-Max-Age: 300
Access-Control-Allow-Origin: *

Content: 135662 bytes

Text: '����JFIFHH��C





)!#-$*9*-13666 (;?:4>0563��C


                                                3""33333333333333333333333333333333333333333333333333�%�"���Q!1A"Qaq�2��#B��R�$3b���r�CS��%4�5cd��&Ts6Dt����
"""
