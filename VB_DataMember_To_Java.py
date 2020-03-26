import os
import sys
import clipboard


class VBParser:
    def __init__(self, parse_type, contents_to_parse):
        self.parse_type = parse_type
        self.un_parsed_contents = contents_to_parse
        self.parsed_contents = []

    def parse_file(self):
        with open(self.un_parsed_contents, 'r') as file:
            self.un_parsed_contents = file.read()
            self.parse_class()

    def parse_class(self):
        self.clean_contents()
        self.parse_contents()

    def clean_contents(self):
        self.un_parsed_contents = self.un_parsed_contents.split('\n')
        self.un_parsed_contents = [x for x in self.un_parsed_contents if x != '\n' and x]

    def parse_contents(self):
        parse_data_member = False
        for line in self.un_parsed_contents:
            if line.strip().startswith('\''):
                continue
            elif line.find("Class") != -1:
                if line.find("End Class") != -1:
                    self.parsed_contents.append("}")
                    continue

                words = line.split(' ')
                line = [x.lower() for x in words[:-1]]
                line.append(words[-1])
                line.append('{')
                line = ' '.join(line)
                self.parsed_contents.append(line)
            elif line.find('DataMember()') != -1:
                parse_data_member = True
                continue
            elif parse_data_member:
                parse_data_member = False
                self.parse_data_member(line)

        self.parsed_contents = '\n'.join(self.parsed_contents)

    def parse_data_member(self, data_member):
        tokens = [x for x in data_member.strip().split(' ', 4) if x.lower() != 'as']
        parsed_data_member = f"\t{tokens[0].lower()} {self.parse_data_type(tokens[-1])} {tokens[2]};"
        self.parsed_contents.append(parsed_data_member)

    def parse_data_type(self, data_type):
        default_index = data_type.find("=")
        if default_index != -1:
            data_type = data_type[:default_index].strip()

        if data_type.lower() in ["boolean", "double", "float"]:
            data_type = data_type.lower()
        elif data_type == "String":
            pass
        elif data_type.lower() in ['integer', 'integer?']:
            data_type = 'int'
        elif data_type.find("Of ") != -1:
            data_type = data_type.replace('(Of ', '<')
            data_type = data_type.replace(')', '>')
        elif data_type.lower() in ['guid']:
            data_type = "UUID"

        return data_type

    def parse(self):
        if self.parse_type == "-file":
            self.parse_file()
        elif parse_type == "-str":
            self.parse_class()
        else:
            print("Invalid parse type")
            exit(-2)

    def output(self, output_type, file_path=None):
        if output_type == 'clipboard':
            clipboard.copy(self.parsed_contents)
        elif output_type == 'file':
            if file_path is None:
                raise Exception("No file path was provided")
            with open(file_path, 'w') as file:
                file.write(self.parsed_contents)
        else:
            print(self.parsed_contents)


def display_help():
    print("\n\n")
    print(f"python {__file__} <parse_type> <content_to_parse> <output_type> <optional_file_path>\n")
    print("<parse_type>:       -file, -str, -dir")
    print("<content_to_parse>: file_path, string, dir_path")
    print("<output_type>:      -console, -clipboard, -file <file_path>")


if __name__ == "__main__":
    arg_count = len(sys.argv)
    output_type = "console"
    output_path = None

    if arg_count > 0 and sys.argv[1] == "--help":
        display_help()
        exit(1)

    if arg_count < 3:
        print("Invalid argument count")
        exit(-1)

    parse_type = sys.argv[1]
    content_to_parse = sys.argv[2]

    if arg_count == 5:
        output_type = sys.argv[3][1:]
        output_path = sys.argv[4]

    items_to_parse = [{}]

    if parse_type == "-dir":
        items_to_parse = [{'parse_type': "-file", 'content_to_parse': os.path.join(content_to_parse, x),
                           'output_type': output_type,
                           'output_path': os.path.join(output_path, os.path.basename(x)[2:].replace(".vb", ".java"))}
                          for x in os.listdir(content_to_parse)]
    else:
        items_to_parse = [{'parse_type': parse_type, 'content_to_parse': content_to_parse, 'output_type': output_type,
                           'output_path': output_path}]

    for item in items_to_parse:
        vb_parser = VBParser(item['parse_type'], item['content_to_parse'])

        vb_parser.parse()
        vb_parser.output(item['output_type'], item['output_path'])
