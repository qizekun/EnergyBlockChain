class Transaction:
    """
    存储交易信息的类
    包括交易发送人，交易接受人，交易数量信息
    """
    def __init__(self,sender1:str,receive1:str,amount1:int,transaction_time:int):
        self.sender=sender1
        self.receiver=receive1
        self.amount=amount1
        self.transaction_time=transaction_time
    def toJsonStr(self):
        return {
            'amount':self.amount,
            'receiver':self.receiver,
            'sender':self.sender,
            'transaction_time':self.transaction_time
        }
    def __eq__(self, other):
        return self.__dict__ == other.__dict__