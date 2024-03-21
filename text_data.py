
class TextData:
    def __init__(self,text) -> None:
        self.lines = text.split('\n')

    def add_line(self,line):
        self.lines.append(line);

    def get_line_count(self):
        return len(self.lines)

    def get_lines_combine(self,start,count):
        line_count = self.get_line_count()
        combine = ''
        if start>line_count or count<=0 or start<0:
            return combine
        line_end = start+count
        if start+count>line_count:
            line_end = line_count

        for i in range(start,line_end):
            combine = combine+self.lines[i]+'\n'
        return combine
    def get_lines(self):
        return self.lines
    def search(self,text):
        ret_list = []
        for index,line in enumerate(self.lines):
            if line.find(text) != -1:
                ret_list.append(index)
        return ret_list
    def combine_search_result(self,lines):
        text_data = TextData('')
        for line_number in lines:
            text_data.add_line(self.lines[line_number])
        return text_data

    def write_to_file(self,file_path):
        with open(file_path,'w') as f:
            for line in self.lines:
                f.write(line+'\n')

