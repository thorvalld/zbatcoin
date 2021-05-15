from zbatcoin import mysql, session
from blockchain import Block, Blockchain


class InvalidTransactionException(Exception):
    pass


class InsufficientFundsException(Exception):
    pass


class Table():
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "(%s)" % ",".join(args)  # format (name,username,email,password)
        self.columnsList = args

        if is_new_table(table_name):
            create_data = ''
            for column in self.columnsList:
                create_data += "%s varchar(100)," % column

            cur = mysql.connection.cursor()
            print('CREATE TABLE %s(%s)' % (self.table, create_data[:len(create_data) - 1]))
            cur.execute("CREATE TABLE %s(%s)" % (self.table, create_data[:len(create_data) - 1]))
            cur.close()

    def fetch_all(self):
        cur = mysql.connection.cursor()
        fetch_result = cur.execute("SELECT * FROM %s" % self.table)
        data = cur.fetchall()
        return data

    def fetch_one(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        fetch_result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" % (self.table, search, value))
        if fetch_result > 0:
            data = cur.fetchone()
        cur.close()
        return data

    def drop_one(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM %s WHERE %s = \"%s\"" % (self.table, search, value))
        mysql.connection.commit()
        cur.close()

    def clear_all(self):
        self.drop_all()
        self.__init__(self.table, *self.columnsList)

    def drop_all(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" % self.table)
        cur.close()

    def insert(self, *args):
        data = ""
        for arg in args:
            data += "\"%s\"," % arg

        cur = mysql.connection.cursor()
        print("INSERT INTO %s%s VALUES(%s)" % (self.table, self.columns, data[:len(data) - 1]))
        cur.execute("INSERT INTO %s%s VALUES(%s)" % (self.table, self.columns, data[:len(data) - 1]))
        mysql.connection.commit()
        cur.close()

    def raw_sql(exec):
        cur = mysql.connection.cursor()
        cur.execute(exec)
        mysql.connection.commit()
        cur.close()


def is_new_table(new_table):
    cur = mysql.connection.cursor()
    try:
        res = cur.execute("SELECT * FROM %s" % new_table)
        cur.close()
    except Exception as ex:
        print(ex)
        return True
    else:
        return False


def is_new_user(username):
    users = Table('users', 'name', 'username', 'email', 'password')
    data = users.fetch_all()
    usernames = [user.get('username') for user in data]

    return False if username in usernames else True


def transfer_funds(sender_username, recipient_username, dispatched_amount):
    try:
        dispatched_amount = float(dispatched_amount)
    except ValueError:
        raise InvalidTransactionException('Invalid Transaction.')

    if dispatched_amount > fetch_balance(sender_username) and sender_username != 'BANK':
        raise InsufficientFundsException('Insufficient Funds: you do not have enough funds in your balance.')
    elif sender_username == recipient_username:
        raise InvalidTransactionException('Invalid Transaction: sender can\'t be the recipient.')
    elif dispatched_amount < 0.00:
        raise InvalidTransactionException('Invalid Transaction: you can\'t send or receive negative funds.')
    elif dispatched_amount == 0.00:
        raise InvalidTransactionException('Invalid Transaction: you can\'t send or receive funds equal to 0.00 ZBT')

    elif is_new_user(recipient_username):
        raise InvalidTransactionException('Invalid Transaction: user does not exist.')

    blockchain = fetch_blockchain()
    number = len(blockchain.chain) + 1
    data = '%s]==>%s]==>%s' % (sender_username, recipient_username, dispatched_amount)
    blockchain.mine(Block(number, data=data))
    synchronise_blockchain(blockchain)


def fetch_balance(username):
    balance = 0.00
    blockchain = fetch_blockchain()
    for block in blockchain.chain:
        data = block.data.split("]==>")
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance


def fetch_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table('blockchain', 'number', 'zbathash', 'previous', 'data', 'nonce')
    for blckchn in blockchain_sql.fetch_all():
        blockchain.push_block_to_chain(
            Block(
                int(blckchn.get('number')),
                blckchn.get('previous'),
                blckchn.get('data'),
                int(blckchn.get('nonce'))
            )
        )

    return blockchain


def synchronise_blockchain(blockchain):
    blockchain_sql = Table('blockchain', 'number', 'zbathash', 'previous', 'data', 'nonce')
    blockchain_sql.clear_all()

    for block in blockchain.chain:
        blockchain_sql.insert(
            str(block.number),
            block.zbathash(),
            block.previous_hash,
            block.data,
            block.nonce
        )


def blockchain_test():
    pass
    """
    --CLEARING CHAIN TEST--
    blockchain_sql = Table('blockchain', 'number', 'zbathash', 'previous', 'data', 'nonce')
    blockchain_sql.clear_all()

    --PUSHING TO CHIN TEST
    blockchain = Blockchain()
    block_data = ["Zbat", "Crypto", "Tanit", "Doge", "Zbatcoin"]
    nbr = 0
    for data in block_data:
        nbr += 1
        blockchain.mine(Block(number=nbr, data=data))

    synchronise_blockchain(blockchain)
    """
