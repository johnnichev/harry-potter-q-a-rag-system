import time
from backend.app.rag import RAGService


def main():
    s = RAGService()
    t0 = time.time()
    ans = s.ask("Where do the Dursleys live?")
    t1 = time.time()
    print("Answer:", ans)
    print("Latency:", round(t1 - t0, 3), "s")


if __name__ == "__main__":
    main()
