from os import rename
from sys import argv
import subprocess
import re
import codecs

# stack of namespaces
stack = [] 

class Namespace:
    def __init__(self, namespace_id):
        self.open_bracket_counter = 0
        self.closing_bracket_counter = 0
        self.namespace_level = 0
        self.namespace_id = namespace_id 

    def update_counters(self,update_open_counter, update_closing_counter):
        print("UPDATE COUNTERS ({2}) {0} {1}".format(update_open_counter, update_closing_counter, self.namespace_id))
        self.open_bracket_counter += update_open_counter
        self.closing_bracket_counter += update_closing_counter
        print("OPEN_BRACKET_COUNTER = {0} && CLOSING_BRACKET_COUNTER = {1}".format(self.open_bracket_counter,self.closing_bracket_counter))

def update_counters(update_open_counter, update_closing_counter):
    for e in stack:
        e.update_counters(update_open_counter, update_closing_counter)

def has_namespace_declaration(string):
    return True if re.search("^namespace.*::.*{.*",string) is not None else False

def convert_namespace_declaration_to_old_style(namespace_decl):
    global stack
    converted_namespaces=[]
    namespaces=[]

    formatted_data_decl = ''
    data_to_add = ''
    add_data = '{' in namespace_decl and '}' in namespace_decl
    if add_data:
        data_to_add = namespace_decl.split('{')[1].split('}')[0].strip() + '\n'

    formatted_namespace_decl = namespace_decl.replace('namespace ','').split('{')[0].strip()
    formatted_namespace_decl = formatted_namespace_decl.split('::')

    # convert namespace
    for e in formatted_namespace_decl:
        converted_namespaces.append("namespace {0} ".format(e) + '{')
    
    # save namespace level
    stack[-1].namespace_level=len(converted_namespaces)
    if add_data:
        # in case of declaration like namespace bla::bla::bla { /* some code */ }
        # it is necessary to write overlapping } scopes
        converted_namespaces.append(data_to_add + format_data(namespace_level))
        stack[-1].namespace_level = 0
    return converted_namespaces[:]

def format_data(data):
    formatted_data=''
    if isinstance(data, int):
        if data > 0:
            formatted_data = '}' * data + '\n'
    elif isinstance(data, list):
        formatted_data = '\n'.join(data) + '\n'
    return formatted_data[:]

def check_namespace_towrite():
    global stack

    if len(stack) == 0:
        return ''
    if stack[-1].open_bracket_counter == stack[-1].closing_bracket_counter and stack[-1].namespace_level != 0:
        string_to_write = format_data(stack[-1].namespace_level)
        stack.pop()
        return string_to_write[:]
    else:
        return ''

def main():
    global stack

    filename = argv[1]
    temp_filename = filename + '.temp'
    string_to_write=''

    with codecs.open(filename, encoding='utf-8') as file, codecs.open(temp_filename,'w', encoding='utf-8') as temp_file:
        for line in file:
            print("GOT LINE: " + line)
            if '{' in line and '\"{\"' not in line:
                update_counters(line.count('{'),0)
            if '}' in line and '\"}\"' not in line:
                update_counters(0,line.count('}'))

            string_to_write = check_namespace_towrite()

            if has_namespace_declaration(line):
                stack.append(Namespace(len(stack)+1))
                update_counters(line.count('{'), line.count('}'))
                string_to_write = format_data(convert_namespace_declaration_to_old_style(line))
            elif string_to_write == '':
                string_to_write = line

            print("STRING_TO_WRITE: " + string_to_write)
            temp_file.write(string_to_write)

        if len(stack) != 0:
            if stack[-1].open_bracket_counter != stack[-1].closing_bracket_counter and stack[-1].namespace_level != 0:
                temp_file.write(format_data(stack[-1].namespace_level - 1))
    rename(temp_filename, filename)


if __name__ == '__main__':
    main()

