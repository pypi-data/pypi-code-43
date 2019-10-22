from padhana.core import DocumentQueryContext, ContentNode


class OutlineAnalysis:

    def __init__(self, document):
        self.root = None
        query_context = DocumentQueryContext(document)
        pages = query_context.root.findall(type_re='^page$')
        self.new_pages = []
        for page in pages:
            content_areas = page.findall(type_re='content-area')
            sorted_content_areas = sorted(content_areas, key=lambda node: (-node.get_y(), node.get_x()))
            new_page = ContentNode(type='page')
            self.__embed_content_areas__(new_page, sorted_content_areas)

            self.new_pages.append(new_page)

        self.document = document

    def get_pages(self):
        return self.new_pages

    def __embed_content_areas__(self, parent, content_areas):

        new_content_areas = []
        content_area_stack = []
        for content_area in content_areas:

            placed = False
            while not placed:
                if len(content_area_stack) == 0:
                    new_content_areas.append(content_area)
                    content_area_stack.append(content_area)
                    placed = True
                elif content_area.get_x() < content_area_stack[-1].get_x():
                    content_area_stack.pop()
                elif content_area.get_x() == content_area_stack[-1].get_x():
                    content_area_stack[-1].children.append(content_area)
                    placed = True
                elif content_area.get_x() > content_area_stack[-1].get_x():
                    content_area_stack[-1].children.append(content_area)
                    content_area_stack.append(content_area)
                    placed = True

        parent.children = new_content_areas
