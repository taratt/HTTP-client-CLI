"""
@author: Tara Saba
"""
# All bonus parts are implemented
import argparse
import signal
import urllib.parse
from tqdm import tqdm
import requests
import sys
import validators
import json
import os
from time import sleep

def input_arguments():
    parser = argparse.ArgumentParser(prog='http CLI')
    parser.add_argument("url", help="The URL of the intended web resource")
    parser.add_argument("-M", "--method", default="GET", help="Specify http method",
                        choices=['GET', 'POST', 'PATCH', 'DELETE', 'PUT'])
    parser.add_argument("-H", "--headers", help="Pass header to the server", action='append')
    parser.add_argument("-Q", "--queries", help="Pass query parameters to the server", action='append')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-D", "--data", help="Specify the body of the http request")
    group.add_argument("--json", help="Pass data in json format")
    group.add_argument("--file", help="Specify file address")
    parser.add_argument("--timeout", default=None, help="Maximum interval of time to wait for response", type= float)
    args = parser.parse_args()
    try:
        validURL = validators.url(args.url.split('/')[0]+"//"+args.url.split('/')[1]+args.url.split('/')[2])
        #validURL2 = validators.url(args.url)
        if not validURL:
            print("http CLI: error: Malformed URL")
            sys.exit()
    except IndexError:
        print("http CLI: error: Malformed URL")
        sys.exit()
    return args

def parse_headers(headers):
    parsedHeaders={}
    if headers != None:
        for headerString in headers:
            for head in headerString.split(','):
                head = head.strip()
                if head.split(':')[0].strip().lower() in parsedHeaders.keys():
                    print("http CLI: warning: {} header is initialized more than once, the later value will be sent to the server".format(head.split(':')[0].strip().lower()))
                parsedHeaders[head.split(':')[0].strip().lower()] = head.split(':')[1].strip()
        return parsedHeaders
    return None



def parse_parameters(queries):
    parsedQueries={}
    if queries != None:
        for queryString in queries:
            for param in queryString.split('&'):
                param = param.strip()
                if param.split('=')[0].strip().lower() in parsedQueries.keys():
                    print("http CLI: warning: {} query parameter is initialized more than once, the later value will be sent to the server".format(param.split('=')[0].strip().lower()))
                parsedQueries[param.split('=')[0].strip().lower()] = param.split('=')[1].strip()
        return parsedQueries
    return None

def keyboardInterruptHandler(signal, frame): # In case server takes long to respond and no timeout is defined
    if os.path.exists("rdat.dat"):
        os.remove("rdat.dat")
    sys.exit()

def send_request(args, headers, queries):
    try:
        method = args.method
        body = None
        if args.data != None:
            body = args.data
            try:
                urllib.parse.parse_qs(body,strict_parsing=True )
            except ValueError:
                print("http CLI: warning: The body is not in url-encoded format")

        elif args.json != None:
            body = args.json
            try:
                json.loads(body)
            except:
                print("http CLI: warning: The body is not in json format")

        elif args.file != None:
            try:
                with open(args.file, 'rb') as f:
                    body = f.read()
            except FileNotFoundError:
                print("http CLI: error: The specified file could not be found")
                sys.exit()
        if headers == None:
            headers = {}

        if 'content-type' not in headers.keys():
            if args.data != None:
                headers['content-type'] = 'application/x-www-form-urlencoded'
            elif args.json != None:
                headers['content-type'] = 'application/json'
            elif args.file != None:
                headers['content-type'] = 'application/octet-stream'


        if method == 'GET':
            response = requests.get(args.url, timeout= args.timeout, headers= headers, params= queries,data= body, stream=True)

        elif method == 'POST':
            response = requests.post(args.url, timeout = args.timeout, headers = headers , params = queries, data= body, stream=True )

        elif method =='PATCH':
            response = requests.patch(args.url, timeout=args.timeout, headers=headers, params=queries, data=body, stream=True)

        elif method == 'PUT':
            response = requests.put(args.url, timeout=args.timeout, headers=headers, params=queries, data=body, stream=True)

        elif method == 'DELETE':
            response = requests.delete(args.url, timeout=args.timeout, headers=headers, params=queries, data= body, stream=True)



        return response
    except requests.exceptions.Timeout:
        progress_bar = tqdm(total=100, unit='iB', unit_scale=True)
        progress_bar.update(50)
        sleep(0.5)
        progress_bar.update(50)
        progress_bar.close()
        print("http CLI: error: The server took longer than the specified timeout to respond")
        sys.exit()

    except requests.exceptions.ConnectionError:
        print("http CLI: error: Failed to establish a connection. Check the URL and try again")
        sys.exit()


def print_response_info(response):
    #print(response.url)
    if response.headers['content-type']== 'image/png':
        #open('received_png.png', 'wb').write(response.content)
        progress('received_png.png', response)
        print_header(response)
        print("** The downloaded png file has been saved in received_png.png")
    elif response.headers['content-type']== 'image/jpeg':
        #open('received_jpeg.jpeg', 'wb').write(response.content)
        progress('received_jpeg.jpeg', response)
        print_header(response)
        print("** The downloaded jpeg file has been saved in received_jpeg.jpeg")
    elif response.headers['content-type']== 'application/pdf':
        #open('received_pdf.pdf', 'wb').write(response.content)
        progress('received_pdf.pdf', response)
        print_header(response)
        print("** The downloaded pdf file has been saved in received_pdf.pdf")
    elif response.headers['content-type']== 'video/webm':
        #open('received_webm.webm', 'wb').write(response.content)
        progress('received_webm.webm', response)
        print_header(response)
        print("** The downloaded video file has been saved in received_webm.webm")
    else:
         # # print("BODY:")
         # # print(response.text)
         # total_size_in_bytes = int(response.headers.get('content-length', 0))
         # block_size = 10
         # progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
         # for data in range(total_size_in_bytes):
         #         progress_bar.update(1)
         #
         # progress_bar.close()
         # print_header(response)
         # print("BODY:")
         # print(response.text)
         progress('rdat.dat', response)
         if os.path.exists("rdat.dat"):
            with open("rdat.dat", 'rb') as f:
                  body = f.read()
            os.remove("rdat.dat")
            print_header(response)
            print("BODY:")
            # this part was copied from models.py and it tries to guess the encoding because the content is already consumed and we need to sortta revive it
            try:
              content = str(body, response.encoding, errors='replace')
            except (LookupError, TypeError):
                 content = str(body, errors='replace')
            print(content)

         else:
             print_header(response)
             print("BODY:")
             print(response.text)


def print_header(response):
    print('HTTP/1.1 {} {}'.format(response.status_code, requests.status_codes._codes[response.status_code][0].upper()))

    for header in response.headers.keys():
        print('{}: {}'.format(header, response.headers[header]))

def progress(file_address, response): #loading and progress bar
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 10
    if total_size_in_bytes != 0:
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(file_address, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()
    else:
        progress_bar = tqdm(total=100, unit='iB', unit_scale=True)
        progress_bar.update(100)
        progress_bar.close()


def main():
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    args = input_arguments()
    headers = parse_headers(args.headers)
    params = parse_parameters(args.queries)
    response = send_request(args, headers, params)
    print_response_info(response)


if __name__ == '__main__':
    main()

#http://www.africau.edu/images/default/sample.pdf
#https://file-examples-com.github.io/uploads/2017/10/file_example_PNG_500kB.png
#python3 httpClientCLI.py https://s1.my-film.pw/Movie/Crazy.Rich.Asians.2018/Crazy.Rich.Asians.2018.720p.BluRay.x265.mkv
#"{\"name\":\"tara\"}"