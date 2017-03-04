# Distributed-Fault-tolerant-hierarchical-file-system-using-FUSE-filesystem

Using the FUSE filesystem worked on previously, implemented Fault Tolerance concepts. A highly scaleable client-server model is designed and implemented that supports advanced features such as server replication for performance and fault tolerance. 

There is only a single client, a single file meta-data server, and multiple replica servers for file data. Each file data replica server stores a copy of each file block.

The system supports a quorum approach – parameters determine the minimum number of servers that need to reply to a read request (Qr, configurable between 1 and Nreplicas) and a write request (Qw=Nreplicas)

The system tolerates the following failure modes:
o Server crash, restart – where one or more servers may fail, and a replacement server may start from a blank slate (i.e. without any file data)
o Data corruption in a single server – where data contents in a server has been be corrupted. Assumption that data corruption errors are only tolerated if Qr >= 3 has been taken into account.

The repair mechanism is done at the server side and is transparent to the client. The system block on a write request if there are unavailable servers, but is able to respond to a read request as long as there are at least Qr servers available.