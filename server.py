import grpc
from concurrent import futures
import time
import threading
from datetime import datetime
import minitwitter_pb2
import minitwitter_pb2_grpc

class MiniTwitterServicer(minitwitter_pb2_grpc.MiniTwitterServicer):
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()

    def SendMessage(self, request, context):
        content = request.content
        if len(content) > 80:
            return minitwitter_pb2.SendMessageResponse(success=False)
        timestamp = int(time.time())
        with self.lock:
            self.messages.append(minitwitter_pb2.Message(content=content, timestamp=timestamp))
        return minitwitter_pb2.SendMessageResponse(success=True)

    def GetMessages(self, request, context):
        n = request.n
        with self.lock:
            total = len(self.messages)
            start = max(0, total - n)
            latest = self.messages[start:][::-1]
        return minitwitter_pb2.GetMessagesResponse(messages=latest)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    minitwitter_pb2_grpc.add_MiniTwitterServicer_to_server(MiniTwitterServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server running on port 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()