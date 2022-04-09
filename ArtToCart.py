import sys
from pathlib import Path
import string

def parseSizeSection(line_iterator):
    while True:
        line = next(line_iterator).strip().replace('\t', ' ')

        # skip if line is empty or a comment
        if line.startswith('//') or line == '':
            continue

        # remove white space between data entries
        size_data = [data_entry for data_entry in line.split(' ') if data_entry != '']

        if len(size_data) != 2:
            if len(size_data) > 2:
                print("Found more than 2 data entries in the size section, skipping file")
            elif len(size_data) < 2:
                print("Found less than 2 data entries in the size section, skipping file")
            return None

        # try to convert to integers
        try:
            size_data = [int(data_entry) for data_entry in size_data]
        except ValueError:
            print("Size value must be an integer, skipping file")
            return None

        # check if all data entries are positive
        for data_entry in size_data:
            if data_entry < 0:
                print("Size value must be a positive integer, skipping file")
                return None

        return size_data


def parseSymbolsSection(line_iterator, size):
    symbols = []

    deb_line = 0
    deb_col = 0

    while True:
        # remove newline character from the line
        line = next(line_iterator).replace('\n', '').replace('\r', '').replace('\t', ' ')

        # skip if line is empty or a comment
        if line.startswith('//') or line.strip() == '':
            continue

        symbols.append([])

        row_iterator = iter(line)

        # parse and append characters to the symbols table
        for character in row_iterator:
            try:
                seperator = next(row_iterator)
                deb_col += 1
            except StopIteration:
                seperator = ' '

            if seperator == ' ':
                symbols[-1].append(character)
            elif seperator in string.hexdigits:
                # use next two characters as a single hex value and convert an int
                try:
                    symbols[-1].append(int(character + seperator, 16))
                except ValueError:
                    print(f"key code did not evaluate to a valid hex value, skipping this file: line {deb_line}, col {deb_col}")
                    return None
            else:
                print("missing space between symbols or character code was not formatted corretly, skipping this file")
                return None

            deb_col += 1

        deb_line += 1

        # check if the length of the row matches the size of the texture
        if len(symbols[-1]) != size[0]:
            if len(symbols[-1]) < size[0]:
                print("found too few elements in the symbols section, skipping this file")
            elif len(symbols[-1]) > size[0]:
                print("found too many elements in the symbols section, skipping this file")
            return None

        # stop when the correct size is reached
        if len(symbols) == size[1]:
            break

    return symbols


def parseColorSection(line_iterator, size, section_name):
    color_data = []

    while True:
        # remove newline character from the line
        line = next(line_iterator).strip().replace('\t', ' ')

        # skip if line is empty or a comment
        if line.startswith('//') or line == '':
            continue

        # remove whitespace between elements
        line = [elem for elem in line.split(' ') if elem != '']

        # make sure the row matches the size of the texture
        if len(line) != size[0]:
            if len(line) < size[0]:
                print(f"found too few elements in the {section_name} section, skipping this file")
            elif len(line) > size[0]:
                print(f"found too many elements in the {section_name} section, skipping this file")
            return None

        color_data.append([])

        # parse values in the row
        for elem in line:
            color_values = [elem[index:index+2] for index in range(0, len(elem), 2)]

            if len(color_values) != 3 and len(color_values) != 4:
                if len(color_values) < 3:
                    print(f"found too few values in an element in the {section_name} section, skipping this file")
                if len(color_values) > 4:
                    print(f"found too many values in an element in the {section_name} section, skipping this file")
                return None

            color_data[-1].append([])

            # convert hex values into integers
            for val in color_values:
                color_data[-1][-1].append(int(val, 16))

            # add missing alpha channel
            if len(color_values) == 3:
                color_data[-1][-1].append(0xFF)
        # stop loop when size is met
        if len(color_data) == size[1]:
            break
    return color_data


def main(files):
    print("converting files ", files, " to .cart files")

    for path in [Path(file_path) for file_path in files]:

        if not path.exists():
            print("WARNING: the file ", path, " does not exist, skipping this file")
            continue

        if not path.suffix == ".art":
            print("WARNING: the file ", path, " is not an Ascii texture file, conversion may fail")

        size_data = None
        symbols_data = None
        foreground_data = None
        background_data = None

        with open(path, 'r', encoding='utf-8') as art_in:

            # size section data

            print("converting ", path, " to a .cart file")

            failed_parse = False

            lines = iter(art_in.readlines())

            try:
                size_data = parseSizeSection(lines)
                if size_data is None:
                    continue

                print("parsed size section")

                symbols_data = parseSymbolsSection(lines, size_data)
                if symbols_data is None:
                    continue

                print("parsed symbols section")

                foreground_data = parseColorSection(lines, size_data, "foreground color")
                if foreground_data is None:
                    continue

                print("parsed foreground color section")

                background_data = parseColorSection(lines, size_data, "background color")
                if background_data is None:
                    continue

                print("parsed background color section")

            except StopIteration as e:
                print("the file has incomplete sections, skipping this file")
                continue

        location = '\\'.join(path.parts[:-1])

        cart_path = f"{location}\\{path.stem}.cart"

        print(f"writing file to {cart_path}")

        with open(cart_path, 'wb') as cart_out:
            # Header
            cart_out.write(b'CART')
            
            for size in size_data:
                cart_out.write(size.to_bytes(8, 'little'))

            for col in zip(zip(*symbols_data), zip(*foreground_data), zip(*background_data)):
                for val in zip(col[0], col[1], col[2]):
                    if type(val[0]) is str:
                        cart_out.write(val[0].encode('utf-8'))
                    else:
                        cart_out.write(val[0].to_bytes(1, 'little'))

                    for color in val[1:]:
                        for c_val in color:
                            cart_out.write(c_val.to_bytes(1, 'little'))
                            
if __name__ == '__main__':
    main(sys.argv[1:])
