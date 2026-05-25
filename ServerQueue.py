#Brayden Burak (7921014)
#COMP 3010 A02, Kristina Zapp
#Assignment 1

import socket
import select
import sys
from collections import deque

try: 
    CLIENT_PORT = int(sys.argv[1])
    WORKER_PORT = int(sys.argv[2])
except Exception as e:
    print("Invalid ports! Using default ports 8000 and 8001.")
    print("Usage: py ServerQueue.py <clientPort> <workerPort>")
    CLIENT_PORT = 8000
    WORKER_PORT = 8001  

#List of jobs, ID for the next job to be added (autoincremented)
jobList = {}
nextJobID = 1

#Queue of IDs, used to track if any jobs are available for workers
waitingQueue = deque()

#Statuses of jobs
STATUS_WAITING = "QUEUED"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETE"

#Setup client listening socket
clientListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientListenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientListenSocket.bind(("0.0.0.0", CLIENT_PORT))
clientListenSocket.listen(5)

#Setup worker listening socket
workerListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
workerListenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
workerListenSocket.bind(("0.0.0.0", WORKER_PORT))
workerListenSocket.listen(5)

#List of sockets to listen to
listenSockets = [clientListenSocket, workerListenSocket]

while True:
    readable_sockets, _, _, = select.select(listenSockets, [], [])
    
    for sock in readable_sockets: #Loop through available sockets
        if sock == clientListenSocket: #New client socket
            conn, addr = clientListenSocket.accept()
            listenSockets.append(conn)
            print(f"Client connected {addr}")
        
        elif sock == workerListenSocket: #New worker socket
            conn, addr = workerListenSocket.accept()
            listenSockets.append(conn)
            print(f"Added worker {addr}")
            
        else:#Previous connection
            try:
                data = sock.recv(1024)
                
                if data: #Safety check for disconnect
                    #Need to split by delimiter "\n", it took an entire
                    #weekend to remember TCP is a "pipe" and that sendall()s
                    #from the worker may arrive at the same time (eg. 2\nGET\n)...
                    arguments = data.decode().split("\n")
                    
                    # Loop through arguments in message
                    for arg in arguments:
                        #Prof said we could assume messages from client will always
                        #be valid, but doing some checks anyways
                        argData = arg.split(" ")
                        operation = argData[0]
                    
                        #-----CHECK OPERATION TYPE-----
                        #Client adding job to queue
                        if operation == "JOB":
                            jobMessage = " ".join(argData[1:])
                            if len(jobMessage) > 1:#Ensure job has a message
                                jobList[nextJobID] = {"message": jobMessage, "status": STATUS_WAITING}
                                waitingQueue.append(nextJobID)
                                sock.sendall((f"{nextJobID}\n").encode())#Send job ID
                                print(f"JOB created {nextJobID} {jobMessage}")
                                nextJobID += 1#Update queue size
                            else:
                                sock.sendall("Job is empty!\n".encode())

                        #Client checking statusf of a job
                        elif operation == "STATUS":
                            jobID = int(" ".join(argData[1:]))
                            if jobID in jobList:# Check if valid job ID
                                status = jobList[jobID]["status"]
                                statusString = f"Status of job {jobID}: {status}\n"
                                sock.sendall(statusString.encode())
                                print(f"Client checked STATUS of JOB {jobID}")
                            else:
                                sock.sendall("Invalid job ID!\n".encode())
                    
                        #Worker getting (pulling) a job
                        elif operation == "GET":
                            if not waitingQueue:#No jobs available
                                sock.sendall("NO\n".encode())
                            else:#Job available!
                                jobID = waitingQueue.popleft()
                                jobList[jobID]["status"] = STATUS_RUNNING
                                jobMessage = jobList[jobID]["message"]

                                response = f"JOB {jobID} {jobMessage}\n"
                                sock.sendall(response.encode())
                                print(f"Sending JOB {jobID} to worker: {sock.getpeername()}")

                        #Worker notifying a jobs completion
                        elif operation == "COMPLETE":
                            jobID = int(argData[1])
                            jobList[jobID]["status"] = STATUS_COMPLETED
                else:#Close the socket upon disconnect
                    print(f"Connection from {sock.getpeername()} closed")
                    listenSockets.remove(sock)
                    sock.close()
                    
            except ValueError:#Covers case for "STATUS "
                sock.sendall("Invalid job ID!\n".encode())
                
            except Exception as e: #Client/Worker unexpected disconnect
                print(f"Worker {sock.getpeername()} Disconnected!")
                listenSockets.remove(sock)
                sock.close()