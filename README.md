<h1>Project - T</h1>
<i>Last updated on 12 Nov 2018</i>

<h2> Blockchain Initialization </h2>
When the blockchain initializes, it transfers to itself some money (eg 100)

<h2>Transactions</h2>
Each transaction has one owner (the one who sends the money) and many recipients<br>
When one sender wants to make some coin transfers, a transaction is initiated. When he is ready,
he submits the transaction which is included in a list of pendingTransactions.
When a block is mined, all the pending transactions are included in this block and the block
of transactions is added to the blockchain.


Transaction rules:
- Let's suppose a sender wants to send money to many recipients. None of the coin transfers
will take place if the sender balance is not enough for the total amount of the coin
transfers</b>
- 

<h2>Transaction Verification </h2>
When the sender wants to make the transaction, he signs it with his private key.
When the block containing the transaction is mined, the transaction is validated 
using the public key. Also, the transaction will not take place if the account balance
of the sender is not enough for the transaction.
Transactions are verified according to the order that they are submitted to the pending
transaction list. If a transaction in a block is verified, then one of the next transactions
in the same block can use the funds from the verified transaction.

<h2>Wallet balances</h2>
To get a wallet balance, one can use the transaction input pool dictionary.
