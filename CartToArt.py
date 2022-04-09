import sys
from pathlib import Path


def readData(path):
    with open(path, 'rb') as file:
        header = file.read(4);

        if header != b'CART':
            print("Missing CART header, skipping this file")
            return None

        size_data = [int.from_bytes(file.read(8), 'little'), int.from_bytes(file.read(8), 'little')]

        texture_data = [[[] for _ in range(size_data[0])] for _ in range(size_data[1])]
        file_data = file.read()

        for x in range(size_data[0]):
            for y in range(size_data[1]):
                symbol = file_data[:4].decode('utf-8', 'ignore')
                symbol_size = len(bytes(symbol[0], 'utf-8'))

                # make sure only the symbol is removed,
                # as there is a chance that a colour value might be converted to another valid symbol
                file_data = file_data[symbol_size:]

                foreground = [int(c_val) for c_val in file_data[:4]]
                file_data = file_data[4:]

                background = [int(c_val) for c_val in file_data[:4]]
                file_data = file_data[4:]

                texture_data[y][x] = [symbol, foreground, background]

    return texture_data, size_data


def convert(files):
    for path in [Path(file_path) for file_path in files]:
        texture_data, size_data = readData(path)

        location = '\\'.join(path.parts[:-1])
        out_path = f"{location}\\{path.stem}.art"

        with open(out_path, 'w', encoding='utf-8') as file:
            # write size section
            file.write("# Size\n")
            file.write(f"{size_data[0]} {size_data[1]}\n\n")

            # write symbols section

            file.write("# Symbol section\n")

            for row in texture_data:
                for val in row:
                    symbol = val[0]

                    # convert to hex value
                    if len(symbol) != 1:
                        # only the first characters should be used here, as it should be kept in the range 0-255
                        hex_value = hex(symbol.encode('utf-8', 'ignore')[0])[2:]
                        symbol = f"{hex_value:02}"

                    file.write(f"{symbol: <2}")
                file.write('\n')

            file.write("\n# Foreground section\n")

            for row in texture_data:
                for val in row:
                    foreground = val[1]

                    for c_val in foreground:
                        file.write(f"{hex(c_val)[2:]:02}")
                    file.write(' ')

                file.write('\n')

            file.write("\n# Background section\n")

            for row in texture_data:
                for val in row:
                    foreground = val[1]

                    for c_val in foreground:
                        file.write(f"{hex(c_val)[2:]:02}")
                    file.write(' ')

                file.write('\n')


if __name__ == '__main__':
    convert(sys.argv[1:])
