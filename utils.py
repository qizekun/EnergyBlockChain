import requests
import json


def add(port, neighbour):
    url = f"http://127.0.0.1:{port}/neighbour/add"
    params = {
        "node": neighbour
    }
    response = requests.post(url=url, params=params, timeout=0.2)
    res = json.loads(response.text)
    # print(res)


def get_info(port):
    url = f"http://127.0.0.1:{port}/chain"
    response = requests.get(url=url, timeout=0.2)
    # print(response.text)
    res = json.loads(response.text)
    print(res)


def transaction(sender, receiver, amount, transaction_time, port, last):
    url = f"http://127.0.0.1:{port}/transaction/new"
    params = {
        "sender": str(sender),
        "receiver": str(receiver),
        "amount": str(amount),
        "transaction_time": str(int(transaction_time)),
        "last": str(last)
    }
    # print(port)
    try:
        response = requests.post(url=url, params=params, timeout=0.2)
        # res = json.loads(response.text)
    except:
        pass
    # print(res)
    

def start_mine(port):
    url = f"http://127.0.0.1:{port}/mine"
    response = requests.get(url=url, timeout=0.2)
    # print(response.text)
    res = json.loads(response.text)
    # print(res)
    

def consensus_port(port):
    url = f"http://127.0.0.1:{port}/consensus"
    response = requests.get(url=url, timeout=0.2)
    res = json.loads(response.text)
    # print(res)


if __name__=="__main__":
    # add(5000, 5001)
    # add(5001, 5000)
    # get_info(5000)
    # transaction(5000, 5001, 10)
    # mine(5000)
    # consensus(5001)
    # get_info(5001)
    add(5000, 5001)
