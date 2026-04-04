from node9 import protect
import time

@protect("bash")
def my_dangerous_tool(cmd):
    print(f"Executing: {cmd}")
    return "Done!"

if __name__ == "__main__":
    print("Testing Node9 Protection... (Make sure your daemon is running!)")
    try:
        # This should trigger a Node9 popup if your daemon is active
        my_dangerous_tool("rm -rf /")
    except Exception as e:
        print(f"Caught by Node9: {e}")