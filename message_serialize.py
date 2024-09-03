from message_serializer.directory import Directory

if __name__ == "__main__":
    # Directory._debug = True
    D = Directory("demo")
    D.validate()
    print(D)
