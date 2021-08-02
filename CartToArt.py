import sys

def readData(path):

    with open(path, 'rb') as file:
        size_data = [int.from_bytes(file.read(8), 'little'), int.from_bytes(file.read(8), 'little')]


        texture_data = file.read()
        encoded_data = texture_data.decode('utf-8', 'ignore')
        print(encoded_data)

def convert(file):
    pass

if __name__ == '__main__':
    convert(sys.argv[1:])
