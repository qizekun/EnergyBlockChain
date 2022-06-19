import hashlib
import json
from Block import Block
import time

from Transaction import Transaction

"""
区块链的简单实现类
完成了区块链的简单操作
"""

def validProof(lastproof:int, proof:int, transactions, timestamp, difficult)->bool:
    """
    验证哈希值是不是满足要求，作为演示需要，这里认为哈希值前面
    有n个0就合格
    :param lastproof:上一个区块的工作量证明
    :param proof: 测试的工作量证明
    :return: 测试的工作量证明是不是满足要求
    """
    test = f'{lastproof}{proof}{transactions}{timestamp}'.encode()
    hashStr = hashlib.sha256(test).hexdigest()
    return hashStr[0:difficult] == "0" * difficult

class EnergyChain:
    publicBlock = Block(0,100000000.00000001,[],520,"创世区块")

    def __init__(self):
        self.transactions = []
        self.chain = [EnergyChain.publicBlock]
        self.difficulty = 6
        self.lasttime = time.time()
        self.isminer = True
        self.mine_num = 5
    
    def createBlock(self, timestamp, proof:int):
        """
        创造新的区块
        :param previusHash:上一个区块的哈希值
        :param proof: 工作量证明
        :return: 返回新的区块
        """
        index = len(self.chain) + 1
        hashValue = self.hash(self.chain[-1])
        block = Block(index,
                      timestamp,
                      self.transactions,
                      proof,hashValue)
        #生成新块之后要新建一个存放交易的列表用于存放新交易
        self.transactions=[]
        #将新生成的区块加入到区块链中
        self.chain.append(block)
        return block

    def addTransaction(self, sender:str, receiver:str, amount:int, transaction_time:int)->int:
        """
        生成新的交易信息，将信息加入到待挖区块中
        :param sender: 交易的发送方
        :param receiver: 交易的接受方
        :param amount: 交易数量
        :param transaction_time: 交易时间
        :return: 返回的是交易要插入的区块的index
        """
        newTransaction=Transaction(sender,receiver,amount,transaction_time).toJsonStr()
        for transactions in self.transactions:
            if transactions == newTransaction:
                return self.lastBlock().index + 1
        self.transactions.append(newTransaction)
        # print(self.transactions)
        print(f'当下正在打包的区块含有{len(self.transactions)}个交易')
        return self.lastBlock().index + 1

    def hash(self,block)->str:
        """
        生成区块的哈希
        :param block: 区块
        :return: 返回的是区块的哈希摘要字符串
        """
        blockInfo=json.dumps(block.toJson(),sort_keys=True).encode()
        return hashlib.sha256(blockInfo).hexdigest()

    def proofWork(self, lastProof:int, transactions, timestamp)->int:
        """
        工作量证明函数：
        :param lastProof:上一个区块的工作量证明。
        :return: 返回工作量证明的值
        """
        proof = 0
        while not validProof(lastProof, proof, transactions, timestamp, self.difficulty):
            proof += 1
        return proof

    def lastBlock(self):
        """
        得到节点区块链的最后一个区块
        :return: 如果当前节点没有区块，返回None
        如果有则返回最后一个区块
        """
        try:
            obj=self.chain[-1]
            return obj
        except:
            return None