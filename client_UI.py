import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import grpc
import datetime
import minitwitter_pb2
import minitwitter_pb2_grpc

class MiniTwitterGUI:
    def __init__(self, master):
        self.master = master
        master.title("MiniTwitter Client")
        master.geometry("600x400")
        
        self.setup_ui()
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = minitwitter_pb2_grpc.MiniTwitterStub(self.channel)

    def setup_ui(self):
        # Frame for sending messages
        send_frame = ttk.LabelFrame(self.master, text="Send Message")
        send_frame.pack(padx=10, pady=5, fill=tk.X)

        self.message_entry = ttk.Entry(send_frame, width=70)
        self.message_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.message_entry.bind("<KeyRelease>", self.update_counter)

        self.char_counter = ttk.Label(send_frame, text="80/80")
        self.char_counter.pack(side=tk.LEFT, padx=5)

        send_btn = ttk.Button(send_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.LEFT, padx=5)

        # Frame for retrieving messages
        get_frame = ttk.LabelFrame(self.master, text="Get Messages")
        get_frame.pack(padx=10, pady=5, fill=tk.X)

        self.num_messages = tk.Spinbox(get_frame, from_=1, to=100, width=5)
        self.num_messages.pack(side=tk.LEFT, padx=5, pady=5)

        get_btn = ttk.Button(get_frame, text="Get Messages", command=self.get_messages)
        get_btn.pack(side=tk.LEFT, padx=5)

        # Display area
        self.display_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.display_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.display_area.configure(state='disabled')

    def update_counter(self, event=None):
        content = self.message_entry.get()
        remaining = 80 - len(content)
        self.char_counter.config(text=f"{remaining}/80")
        self.char_counter.config(foreground='red' if remaining < 0 else 'black')

    def send_message(self):
        content = self.message_entry.get().strip()
        if not content:
            messagebox.showwarning("Warning", "Message cannot be empty!")
            return
            
        if len(content) > 80:
            content = content[:80]
            self.message_entry.delete(0, tk.END)
            self.message_entry.insert(0, content)
            
        def send_thread():
            try:
                response = self.stub.SendMessage(
                    minitwitter_pb2.SendMessageRequest(content=content)
                )
                self.master.after(0, lambda: messagebox.showinfo(
                    "Success" if response.success else "Error",
                    "Message sent successfully!" if response.success else "Failed to send message!"
                ))
            except grpc.RpcError as e:
                self.master.after(0, lambda: messagebox.showerror(
                    "Connection Error", f"Failed to connect to server: {e.code()}"))

        threading.Thread(target=send_thread, daemon=True).start()

    def get_messages(self):
        try:
            n = int(self.num_messages.get())
            if n <= 0:
                messagebox.showwarning("Warning", "Number must be positive!")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Invalid number!")
            return

        def get_thread():
            try:
                response = self.stub.GetMessages(
                    minitwitter_pb2.GetMessagesRequest(n=n))
                self.master.after(0, self.display_messages, response.messages)
            except grpc.RpcError as e:
                self.master.after(0, lambda: messagebox.showerror(
                    "Connection Error", f"Failed to connect to server: {e.code()}"))

        threading.Thread(target=get_thread, daemon=True).start()

    def display_messages(self, messages):
        self.display_area.configure(state='normal')
        self.display_area.delete(1.0, tk.END)
        
        if not messages:
            self.display_area.insert(tk.END, "No messages found\n")
        else:
            for i, msg in enumerate(messages):
                dt = datetime.datetime.fromtimestamp(msg.timestamp)
                self.display_area.insert(tk.END, 
                    f"{i+1}. [{dt.strftime('%Y-%m-%d %H:%M:%S')}] {msg.content}\n")
        
        self.display_area.configure(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    app = MiniTwitterGUI(root)
    root.mainloop()