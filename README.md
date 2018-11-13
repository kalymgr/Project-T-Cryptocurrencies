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
- Let's suppose a sender wants to send money to many recipients. Then a list of the coin
transfers is made. The list of coin transfers will start executing until a coin transfer is
found that surpasses the sender account total. <b>This functionality may change, depending on 
the needs.</b>

<h2>Transaction Verification </h2>
When the sender wants to make the transaction, he signs it with his private key.
When the block containing the transaction is mined, the transaction is validated (check if the sender
has enough money) using the public key.

<h2>Wallet balances</h2>
When a transaction is verified, the wallet balances of the sender and the receivers are altered.
