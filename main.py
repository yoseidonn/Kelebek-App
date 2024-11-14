if __name__ == "__main__":
    import os, dotenv
    from dotenv import load_dotenv
    load_dotenv()
    os.environ["BASE_DIR"] = os.getcwd()
    import App