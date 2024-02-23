import math


class Pagination():

    def __init__(self, page, number, obj_num, request=None):
        self.page = page  # 当前页码
        self.number = number  # 每页显示的数量
        self.obj_num = obj_num  # 总共数量的对象
        self.request = request

        # self.start_ = None
        # self.end_ = None

    @property
    def start(self):
        return (self.page - 1) * self.number

    @property
    def end(self):
        end_ = self.start + self.number
        return end_ if end_<= self.obj_num else self.obj_num

    @property
    def page_html(self):
        request_copy = self.request.GET.copy()
        request_copy._mutable = True
        if 'page' in request_copy:
            request_copy.pop('page')
        sift = request_copy.urlencode()

        html_content = """<nav aria-label="...">
                    <ul class="pagination">"""
        if self.page == 1:
            html_content += "<li class='disabled'><span aria-hidden='true'>上一页</span></li>"
        else:
            html_content += f"<li><a href='?page={self.page-1}{f'&{sift}' if sift else ''}' aria-label='Previous'><span aria-hidden='true'>上一页</span></a></li>"

        total_page = math.ceil(self.obj_num / self.number)
        for i in range(1,total_page+1):
            if self.page == i:
                html_content += f'<li class="active"><a href="?page={i}">{i}<span class="sr-only">(current)</span></a></li>'
            else:
                html_content += f"<li><a href='?page={i}{f'&{sift}' if sift else ''}'>{i}</a></li>"

        if total_page == self.page or self.obj_num == 0:
            html_content += '<li class="disabled"><span aria-hidden="true">下一页</span></li>'
        else:
            html_content += f"<li><a href='?page={self.page+1}{f'&{sift}' if sift else ''}' aria-label='Next'><span aria-hidden='true'>下一页</span></a></li>"

        html_content += f'<li class="disabled"><span aria-hidden="true"> 共{self.obj_num}条数据，页码{self.page}/{total_page} </span></li></ul></nav>'

        return html_content


