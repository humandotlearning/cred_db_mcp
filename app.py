from src.cred_db_mcp_server.main import create_demo

demo = create_demo()

if __name__ == "__main__":
    demo.launch(mcp_server=True)
