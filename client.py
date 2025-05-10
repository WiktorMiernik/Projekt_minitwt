import grpc
import datetime
import minitwitter_pb2
import minitwitter_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = minitwitter_pb2_grpc.MiniTwitterStub(channel)
    print("MiniTwitter Client. Commands: 'send <message>', 'get <n>', 'exit'")
    while True:
        cmd = input("> ").strip()
        if cmd.lower() == 'exit':
            break
        parts = cmd.split(maxsplit=1)
        if not parts:
            continue
        if parts[0].lower() == 'send':
            if len(parts) < 2:
                print("Error: Message content required")
                continue
            content = parts[1]
            if len(content) > 80:
                content = content[:80]
                print("Warning: Message truncated to 80 characters")
            response = stub.SendMessage(minitwitter_pb2.SendMessageRequest(content=content))
            print("Message sent" if response.success else "Failed to send message")
        elif parts[0].lower() == 'get':
            if len(parts) < 2:
                print("Error: Number of messages required")
                continue
            try:
                n = int(parts[1])
                if n <= 0:
                    print("Error: n must be positive")
                    continue
                response = stub.GetMessages(minitwitter_pb2.GetMessagesRequest(n=n))
                if not response.messages:
                    print("No messages found")
                else:
                    for i, msg in enumerate(response.messages):
                        dt = datetime.datetime.fromtimestamp(msg.timestamp)
                        print(f"{i+1}. [{dt.strftime('%Y-%m-%d %H:%M:%S')}] {msg.content}")
            except ValueError:
                print("Error: Invalid number")
        else:
            print("Error: Unknown command")

if __name__ == '__main__':
    run()