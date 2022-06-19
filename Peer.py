import hashlib
import json
from argparse import ArgumentParser
from mmap import PROT_READ
from re import S, T
import requests
from flask import Flask, jsonify,request

from Block import Block
from EnergyChain import EnergyChain, validProof
from Transaction import Transaction
from utils import transaction, add, get_info, start_mine, consensus_port
from threading import Thread
import time


class Peer:
    def __init__(self):
        #初始化这个节点的链
        self.blockchain=EnergyChain()
        #初始化这个节点的邻居节点
        self.neighbours = []
        self.address = 0
        self.mining = False
        self.check = False
    
    def setAddress(self,addr):
        self.address=addr
    
    def addNeighbour(self,neighbour):
        """
        给这个节点添加一个邻居
        :param neighbour: 这个邻居的地址信息：5001
        :return: 无
        """
        self.neighbours.append(neighbour)

    def addTransaction(self, last, sender, receiver, amount, transaction_time):
        for port in self.neighbours:
            if str(port) == str(last):
                continue
            transaction(sender, receiver, amount, transaction_time, port, self.address)
        sender = "http://127.0.0.1:" + str(sender)
        receiver = "http://127.0.0.1:" + str(receiver)
        if self.blockchain.isminer:
            self.blockchain.addTransaction(sender, receiver, int(amount), transaction_time)
        if len(self.blockchain.transactions) >= self.blockchain.mine_num:
            print("开始挖矿")
            self.mining = True
            # start_mine(self.address)
            last_block=self.blockchain.lastBlock()
            last_proof=last_block.proof
            timestamp = time.time()
            state, proof=self.proofWork(last_proof, self.blockchain.transactions, timestamp)

            if state:
                self.blockchain.createBlock(timestamp, proof)
                self.blockchain.transactions = []
                self.mining = False
                # 向邻居节点发送新的区块
                for port in self.neighbours:
                    try:
                        url = f"http://127.0.0.1:{port}/check"
                        response = requests.get(url=url, timeout=2)
                    except:
                        pass
                print("挖矿成功")
                time.sleep(1)
                # 挖矿奖励：
                transaction(sender="区块链系统",receiver=f'http://127.0.0.1:{peer.address}', amount=1, transaction_time=time.time(), port=peer.address, last=peer.address)
            else:
                self.mining = False
                self.blockchain.transactions = []
                print("挖矿失败, 被抢矿了")

    def proofWork(self, lastProof:int, transactions, timestamp)->int:
        """
        工作量证明函数：
        :param lastProof:上一个区块的工作量证明。
        :return: 返回工作量证明的值
        """
        proof = 0
        while not validProof(lastProof, proof, transactions, timestamp, self.blockchain.difficulty):
            proof += 1
            if self.check:
                self.check = False
                return False, proof
        return True, proof

    def validChain(self, chain)->bool:
        """
        确定链是不是有效的，只需要查看工作量证明是不是有问题就好
        :param chain: 一个区块链
        :return: 区块链有效的话返回true，否则返回False
        """
        # print("验证区块链")
        index = 1
        length = len(chain)
        lastBlock = chain[0]
        while index < length:
            block = chain[index]
            # 检查哈希值是不是正确
            lastBlockHash = hashlib.sha256(json.dumps(lastBlock).encode()).hexdigest()
            if block['previous_Hash'] != lastBlockHash:
                return False
            # 检查工作量证明是不是正确
            if not validProof(lastBlock['proof'], block['proof'], block['transactions'], block['timestamp'], self.blockchain.difficulty):
                print("工作量证明错误")
                return False
            lastBlock=block
            index+=1
        return True
    def resolveConflicts(self)->bool:
        """
        实现共识算法：
        使用网络中最长的链作为最终链
        :return:  如果节点的链被取代，则返回True，否则返回False
        """
        # print("开始解决冲突")
        newChain = None
        # 寻找比自己长的链，比自己短的链不去管它，这由共识算法决定
        maxLen = len(self.blockchain.chain)
        # 遍历所有的邻居节点，判断邻居节点的链和自己的异同
        # 如果邻居节点的链比自己的长，并且链是合法的，将这条链暂存起来作为最终
        # 候选链，遍历结束后得到的候选链就是节点网络中 最长的一个链

        for node in self.neighbours:
            response=requests.get(
                f'http://127.0.0.1:{node}/chain')
            if response.status_code == 200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length > maxLen and self.validChain(chain):
                    maxLen = length
                    newChain = chain
        if newChain:
            self.blockchain.chain=[]
            for temp in newChain:
                transactions=[]
                transet=temp['transactions']
                for t in transet:
                    transactions.append(Transaction(t['sender'],t['receiver'],int(t['amount']),t['transaction_time']).toJsonStr())
                self.blockchain.chain.append(
                    Block(temp['index'],temp['timestamp'],transactions,temp['proof'],temp['previous_Hash'])
                )
            return True
        return False
    
    def auto(self):
        while True:
            time.sleep(20)
            # print("主动查找邻居节点")
            for port in range(10000):
                if not port in self.neighbours and port != self.address:
                    try:
                        url = f"http://127.0.0.1:{port}/check"
                        response = requests.get(url=url, timeout=2)
                        if response.status_code == 200:
                            print(f"主动搜寻添加邻居节点{port}成功")
                            self.addNeighbour(port)
                    except:
                        pass
            if self.resolveConflicts():
                print("链被取代")
    
    def auto_find(self):
        Thread(target=self.auto,args=()).start()

peer=Peer()
app=Flask(__name__)

@app.route("/chain",methods=['GET'])
def getChian():
    """
    获取该节点区块链上的所有区块的信息
    :return: 返回区块的信息和请求状态码
    """
    temp=peer.blockchain.chain
    json_chain=[]
    for block in temp:
        json_chain.append(block.toJson())
    response={
        'chain':json_chain,
        'length':len(temp)
    }
    return jsonify(response), 200
@app.route('/transaction/new',methods=['POST'])
def addNewTransaction():
    """
    添加新的交易到当前节点的区块中
    :return: 返回提示信息
    """
    #检查提交的参数是不是完整，不完整返回错误:
    sender = request.values.get("sender")
    receiver = request.values.get("receiver")
    amount = request.values.get("amount")
    transaction_time = request.values.get("transaction_time")
    last = request.values.get("last")
    if sender == None or receiver == None or amount == None:
        return "您发送的请求参数不完整，无法操作", 400
    index = peer.addTransaction(last, sender, receiver, int(amount), transaction_time)
    response = {
        "服务器消息": "添加成功",
        "所在区块索引": index
    }
    return jsonify(response), 200

@app.route("/mine", methods=['GET'])
def mine():
    """
    挖矿产生新的区块：
    :return: 返回http response
    """
    last_block = peer.blockchain.lastBlock()
    last_proof = last_block.proof
    timestamp = time.time()
    proof=peer.blockchain.proofWork(last_proof, peer.blockchain.transactions, timestamp)

    block = peer.blockchain.createBlock(timestamp, proof)

    response={
        "message":"新的区块形成了",
        "index":block.index,
        "transactions":[t.toJsonStr()
                        for t in block.transactions],
        "proof":block.proof,
        "previous_Hash":block.previous_Hash
    }
    # 挖矿奖励：
    transaction(sender="区块链系统",receiver=f'http://127.0.0.1:{peer.address}',amount=1,transaction_time=time.time(), port=peer.address, last=peer.address)

    return jsonify(response), 200

@app.route("/neighbour/add",methods=['POST'])
def addNeighbour():
    """
    接受前端传过来的值，加入到自己的邻居节点中
    :return: 返回响应的消息
    """
    node=request.values.get("node")
    if node==None:
        return "您的请求缺少参数，无法处理",400
    peer.addNeighbour(node)
    response={
        "服务器返回信息":"添加peer邻居成功！",
        "节点地址":peer.address,
        "邻居节点数量":len(peer.neighbours)
    }
    return jsonify(response), 200

@app.route("/consensus",methods=['GET'])
def consensus():
    replaced = peer.resolveConflicts()
    if replaced:
        response={
            "message":"链条被更新",
            "length":len(peer.blockchain.chain)
        }
    else:
        response={
            "message":"保持链条不变",
            "length":len(peer.blockchain.chain)
        }
    return jsonify(response),201

@app.route("/check",methods=['GET'])
def check():
    response={
        "message":"节点存在",
    }
    if peer.resolveConflicts():
        peer.check = True
        print("链被取代")
    return jsonify(response),200


def run(port):
    while True:
        instruction = input()
        info = instruction.split(" ")
        # try:
        if 'a' == info[0]:
            neighbour = int(info[1])
            add(port, neighbour)
        elif 'i' == info[0]:
            get_info(port)
        elif 't' == info[0]:
            if len(info) == 3:
                sender = port
                receiver = info[1]
                amount = info[2]
                transaction(sender, receiver, amount, time.time(), port, port)
            elif len(info) == 4:
                sender = info[1]
                receiver = info[2]
                amount = info[3]
                transaction(sender, receiver, amount, time.time(), port, port)
        elif 'm' in instruction:
            start_mine(port)
        elif 'c' in instruction:
            consensus_port(port)
        # except:
                # print('输入格式错误，请重新输入')


if __name__ == '__main__':
    """
    实现区块链 p2p 网络，构造多个peer节点：
    """
    parser=ArgumentParser()
    parser.add_argument("-p","--port",default=5000,type=int,help="监听的端口") 
    port=parser.parse_args().port
    peer.setAddress(port)
    peer.auto_find()
    Thread(target=run,args=(port,)).start()
    app.run(host='127.0.0.1',port=port)
    

    
