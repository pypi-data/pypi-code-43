import numpy as np

from padhana.core import DocumentQueryContext, ContentNode, Document, AttributeDict


class BaseLayoutAnalysis:

    def build_pages(self):
        # We will start by creating a content area with all the text in it
        # then we will aim to determine if that should be more than one content
        # area - then we will rinse and repeat
        # page_index_list = [12]
        # for page_index in page_index_list:
        for page_index in range(len(self.all_raw_pages)):
            raw_page = self.all_raw_pages[page_index]
            self.pages.append(Page(raw_page, self))

    def get_structure(self):
        result = ContentNode(type='root')
        for page in self.pages:
            new_node = ContentNode(type='page')
            for content_area in page.content_areas:
                if content_area.lines:
                    content_area_node = ContentNode(type='content-area',
                                                    bbox=[content_area.lines[0].get_x(), content_area.lines[0].get_y()])
                    for line in content_area.lines:
                        content_area_line = line.to_content_node()

                        if content_area_line.value.strip():
                            content_area_node.children.append(content_area_line)
                    new_node.children.append(content_area_node)

            result.children.append(new_node)
        return result

    def get_document(self):
        return Document(self.document.metadata, self.get_structure())


class LineLayoutAnalysis(BaseLayoutAnalysis):

    def __init__(self, document):
        self.document = document
        self.query_context = DocumentQueryContext(document)
        self.all_raw_pages = self.query_context.root.findall(type_re='^page$')
        self.pages = []

        self.build_pages()


class TextLayoutAnalysis(BaseLayoutAnalysis):

    def __init__(self, document):
        self.document = document
        self.query_context = DocumentQueryContext(document)
        self.all_raw_pages = self.query_context.root.findall(type_re='^page$')
        self.pages = []

        self.build_pages()


class Word:
    """
    A word represents a collection of characters
    that we have isolated and believe, based on the layout of the page
    to be a word
    """

    def __init__(self):
        self.text_nodes = []
        self.text = ''

    def add_nodes(self, text_nodes):
        self.text_nodes.extend(text_nodes)
        self.text = self.as_string()

    def as_string(self):
        s = ""
        for text_node in self.text_nodes:
            s += text_node.get_value()

        return s

    def get_x(self):
        if self.text_nodes:
            return self.text_nodes[0].get_x()
        else:
            return None

    def get_y(self):
        if self.text_nodes:
            return self.text_nodes[0].get_y()
        else:
            return None

    def get_width(self):
        if self.text_nodes:
            return self.text_nodes[-1].get_x() + self.text_nodes[-1].get_width() - self.text_nodes[0].get_x()
        else:
            return None

    def get_height(self):
        if self.text_nodes:
            return self.text_nodes[0].get_height()
        else:
            return None


class Line:
    """
    A line is made up of text nodes
    Initializing a line is done by giving it an array of text_nodes

    """

    def __init__(self, text_nodes):
        # Remove the first and last nodes if they are empty strings or spaces
        self.text_nodes = text_nodes
        self.words = []
        self.text = ''
        self.statistics = NodeStatistics(self.text_nodes)

    def includes(self, text_node):
        line_statistics = NodeStatistics(self.text_nodes)
        # If the text_node overlaps with a current non-space node in line, return False
        for n in self.text_nodes:
            if text_node.get_x() <= n.get_x() + n.get_width() - line_statistics.updated_mean_width and \
                    text_node.get_x() + text_node.get_width() >= n.get_x() and len(n.get_value().strip()) > 0 and \
                    len(text_node.get_value().strip()) > 0:
                return False

        # If ys are equal or overlap by more than half of the height
        return text_node.get_y() == self.text_nodes[0].get_y() or \
               (abs(text_node.get_y() - self.text_nodes[0].get_y()) <= self.text_nodes[0].get_height() * 0.5) or \
               (abs(text_node.get_y() - self.text_nodes[0].get_y()) <= text_node.get_height() * 0.5)

    def add_node(self, text_node):
        self.text_nodes.append(text_node)

    def add_nodes(self, text_nodes):
        self.text_nodes.extend(text_nodes)

    def as_string(self):
        s = ""
        for word in self.words:
            s += word.as_string() + " "

        return s.strip()

    def to_content_node(self):
        content_node = ContentNode(type='line', bbox=[self.get_x(), self.get_y()], value=self.as_string())

        # for word in self.words:
        #     content_node.children.append(ContentNode(type='word', value=word.as_string()))

        return content_node

    def get_x(self):
        if len(self.words) > 0:
            return self.words[0].get_x()
        else:
            return None

    def get_y(self):
        if len(self.words) > 0:
            return self.words[0].get_y()
        else:
            return None

    def get_width(self):
        if len(self.words) > 0:
            return self.words[-1].get_x() + self.words[-1].get_width() - self.words[0].get_x()
        else:
            return None

    def get_height(self):
        if len(self.words) > 0:
            return self.words[0].get_height()
        else:
            return None

    def build_words(self):
        self.words = []
        self.text = ''
        if len(self.text_nodes) > 0:
            # Need to resort text_nodes based on x since a slop was used in grouping the
            # text_nodes into a line
            self.text_nodes = sorted(self.text_nodes, key=lambda node: (node.get_x()))

            # First let's work out the mean distance between text_nodes
            # Since the text_nodes contain just characters,
            # if the space between two text_nodes is more than the mean,
            # then it is part of another word

            statistics = NodeStatistics(self.text_nodes)
            self.statistics = statistics

            # Now we go over each of the text_nodes and break them
            # into words
            last_x = self.text_nodes[0].get_x()
            last_width = 0.0
            current_word = Word()
            for node in self.text_nodes:
                if node.get_value().isspace():
                    if current_word.text_nodes:
                        self.words.append(current_word)
                    current_word = Word()
                else:
                    if abs(node.get_x() - last_x - last_width) > statistics.updated_mean_width:
                    # if abs(node.get_x() - last_x - last_width) > statistics.updated_mean_space_width:
                        # Start new word
                        if current_word.text_nodes:
                            self.words.append(current_word)
                        current_word = Word()

                    current_word.add_nodes([node])
                last_x = node.get_x()
                last_width = node.get_width()
            if current_word.text_nodes:
                self.words.append(current_word)

            self.text = self.as_string()

    def get_spaces(self):
        # This gets all the TextSpaces in the line - and the x1 and x2 of the space
        # Each space is [width, x1, x2]

        spaces = []
        if len(self.words) > 1:
            prev_word = self.words[0]
            for word in self.words[1:]:
                new_space = TextSpace(word.get_x() - prev_word.get_x() - prev_word.get_width(),
                                      prev_word.get_x() + prev_word.get_width(), word.get_x())
                spaces.append(new_space)
                prev_word = word
        return spaces


class Page:
    """
    A page is made up of content areas

    """

    def __init__(self, page_node, parent):
        self.node = page_node
        self.width = page_node.get_width()
        self.height = page_node.get_height()

        # Get all text nodes
        self.text_nodes = page_node.findall(type_re='text')

        # Get all image nodes

        # For the page's statistics, only get the non-space text_nodes
        non_space_text_nodes = [node for node in self.text_nodes if
                                not (node.get_value().isspace() or node.get_value() == '')]
        self.statistics = NodeStatistics(non_space_text_nodes)

        self.content_areas = []

        # First, check if there is a bit with 2 columns as opposed to just 1
        # The order of the lines will vary based on this information
        if isinstance(parent, TextLayoutAnalysis):
            initial_content_area_lines = self.check_for_text_columns()
        else:
            initial_content_area_lines = ContentArea(self.text_nodes).lines

        # Check for superscripts - if found, merge with the line after it
        # Will leave the superscripts where they are
        initial_content_area_lines = self.check_for_superscripts(initial_content_area_lines)

        # Next, group these lines into content areas
        if len(initial_content_area_lines) > 0:
            self.group_lines_to_content_areas(initial_content_area_lines)

        # Insert the images in content_areas
        image_nodes = page_node.findall(type_re="figure")
        if len(image_nodes) > 0:
            self.insert_image_nodes(image_nodes)

    def check_for_text_columns(self):
        initial_content_area = ContentArea(self.text_nodes)
        # How we have a single content area - we will go through all the lines and determine how
        # many content areas we really have

        initial_content_area_lines = []
        first_column_lines = []
        second_column_lines = []
        two_column_marker_found = False
        prev_col_space = TextSpace(self.width, 0.0, self.width)
        mid_col_space = TextSpace(self.width/7.0, self.width * 3.0/7.0, self.width * 4.0/7.0)

        for line in initial_content_area.lines:
            # Check if there is a space that is in the middle with more than 3x the updated_mean_width
            spaces = line.get_spaces()
            col_spaces = [space for space in spaces if space.width > 4.0 * self.statistics.updated_mean_width and
                          space.spaces_overlap(mid_col_space) and
                          space.spaces_overlap(prev_col_space)]
            # The column space is somewhere that is more than a third of the page (just for 2 columns)

            if len(line.as_string().strip()) == 0:
                # If text is empty, don't process
                continue

            elif len(col_spaces) == 1:
                two_column_marker_found = True
                col_space = col_spaces[0] # Just get the first one
                # There are 2 columns
                first_column_text_nodes = [node for node in line.text_nodes if node.get_x() < col_space.x1]
                second_column_text_nodes = [node for node in line.text_nodes if node.get_x() >= col_space.x2]

                first_column_line = Line(first_column_text_nodes)
                first_column_line.build_words()
                first_column_lines.append(first_column_line)

                second_column_line = Line(second_column_text_nodes)
                second_column_line.build_words()
                second_column_lines.append(second_column_line)

                prev_col_space = col_space.spaces_overlap(prev_col_space)

            elif two_column_marker_found:

                if line.words[-1].get_x() + line.words[-1].get_width() < prev_col_space.x2:
                    # Still two columns - just on the first column
                    first_column_lines.append(line)
                    second_col_space = TextSpace(self.width - (line.words[-1].get_x() + line.words[-1].get_width()),
                                                 line.words[-1].get_x() + line.words[-1].get_width(), self.width)
                    prev_col_space = second_col_space.spaces_overlap(prev_col_space)

                elif line.words[0].get_x() >= prev_col_space.x1:
                    # Still two columns - just on the second column
                    second_column_lines.append(line)
                    first_col_space = TextSpace(line.words[0].get_x(), 0.0, line.words[0].get_x())
                    prev_col_space = first_col_space.spaces_overlap(prev_col_space)

                else:
                    # This is the end of two columns - will just add everything to second column
                    two_column_marker_found = False
                    second_column_lines.append(line)
                    initial_content_area_lines.extend(first_column_lines)
                    initial_content_area_lines.extend(second_column_lines)
                    first_column_lines = []
                    second_column_lines = []
                    prev_col_space = TextSpace(self.width, 0.0, self.width)

            else:
                # This is just one column
                first_column_lines.append(line)

        initial_content_area_lines.extend(first_column_lines)
        initial_content_area_lines.extend(second_column_lines)

        return initial_content_area_lines

    def check_for_superscripts(self, initial_content_area_lines):
        superscript_lines = [(l_idx, l) for l_idx, l in enumerate(initial_content_area_lines)
                             if l.as_string().isdigit() and
                             l.get_height() < self.statistics.updated_mean_height * 0.75]

        for index_and_line in superscript_lines:
            l_idx = index_and_line[0]
            line = index_and_line[1]
            next_line = initial_content_area_lines[l_idx + 1] \
                if l_idx < len(initial_content_area_lines) - 1 else None

            # Combine the two lines
            if next_line:
                new_text_nodes = line.text_nodes + next_line.text_nodes
                new_next_line = Line(new_text_nodes)
                new_next_line.build_words()
                initial_content_area_lines[l_idx + 1] = new_next_line

        return initial_content_area_lines


    def group_lines_to_content_areas(self, initial_content_area_lines):
        page_statistics = NodeStatistics(initial_content_area_lines)

        last_line = initial_content_area_lines[0]
        last_line_statistics = NodeStatistics(last_line.text_nodes)
        last_x_y_height = [initial_content_area_lines[0].get_x(), initial_content_area_lines[0].get_y(),
                           last_line_statistics.updated_mean_height]
        current_content_area_lines = []
        current_content_area_text_nodes = []

        if page_statistics.updated_mean_line_space_height is None:
            print('hello')
        if self.statistics.updated_mean_height is None:
            print('hello')

        for line in initial_content_area_lines:
            if len(line.as_string().strip()) > 0:
                line_statistics = NodeStatistics(line.text_nodes)
                if abs(last_x_y_height[1] - line_statistics.mean_y) > \
                        page_statistics.updated_mean_line_space_height * 1.25 or \
                        abs(last_x_y_height[2] - line_statistics.updated_mean_height) > \
                        0.05 * max(last_x_y_height[2], line_statistics.updated_mean_height) and not \
                        (last_line.as_string().isdigit() and
                         last_line.text_nodes[0].get_height() <= 0.75 * self.statistics.updated_mean_height):
                    # If the spacing is more than the updated_mean_height
                    # Or if the font heights are different (more than 95% diff)
                    # And last line is not a superscript used for footers
                    if len(current_content_area_lines) > 0:
                        new_content_area = ContentArea([])
                        new_content_area.lines = current_content_area_lines
                        new_content_area.text_nodes = current_content_area_text_nodes
                        self.content_areas.append(new_content_area)
                    current_content_area_lines = []
                    current_content_area_text_nodes = []

                current_content_area_lines.append(line)
                current_content_area_text_nodes.extend(line.text_nodes)

                last_x_y_height = [line.get_x(), line_statistics.mean_y, line_statistics.updated_mean_height]
            last_line = line

        if len(current_content_area_lines) > 0:
            new_content_area = ContentArea([])
            new_content_area.lines = current_content_area_lines
            self.content_areas.append(new_content_area)

    def insert_image_nodes(self, image_nodes):
        if len(image_nodes) == 0:
            return

        image_nodes = sorted(image_nodes, key=lambda img_node: (-img_node.get_y(), img_node.get_x()))

        image_node = image_nodes[0]
        prev_ca = None
        img_idx = 0

        for ca_idx, content_area in enumerate(self.content_areas):
            # y starts at 0 at the bottom of the page
            if (not prev_ca and image_node.get_y() >= content_area.get_y()) or \
                    (prev_ca and prev_ca.get_y() >= image_node.get_y() >= content_area.get_y()):
                image_content_area = ContentArea([])
                image_content_area.features.image_node = image_node
                self.content_areas.insert(ca_idx, image_content_area)
                img_idx += 1

                if img_idx == len(image_nodes):
                    break
                image_node = image_nodes[img_idx]

            prev_ca = content_area

        # If there are image nodes that are not yet added to content_areas
        while img_idx < len(image_nodes):
            img_content_area = ContentArea([])
            image_node = image_nodes[img_idx]
            img_content_area.features.image_node = image_node
            self.content_areas.append(img_content_area)
            img_idx += 1


class TextSpace:
    """
    A text space contains [width, x1, and x2]
    """
    def __init__(self, width, x1, x2):
        self.width = width
        self.x1 = x1
        self.x2 = x2

    def spaces_overlap(self, space2):
        # This returns the overlap between the two given spaces
        if (self.x1 <= space2.x2 and self.x2 >= space2.x1) or (space2.x1 <= self.x2 and space2.x2 >= self.x1):
            overlap_x1 = max(self.x1, space2.x1)
            overlap_x2 = min(self.x2, space2.x2)
            return TextSpace(overlap_x2 - overlap_x1, overlap_x1, overlap_x2)
        return None


class ContentArea:
    """
    A content area is made up of lines
    """

    def __init__(self, text_nodes):
        if len(text_nodes) > 0:
            self.text_nodes = sorted(text_nodes, key=lambda node: (-node.get_y(), node.get_x()))

            self.lines = []
            self.__build_lines__()

            for line in self.lines:
                line.build_words()

            self.statistics = NodeStatistics(self.lines)

        else:
            self.text_nodes = []
            self.lines = []
            self.statistics = None

        self.features = AttributeDict()

    def __build_lines__(self):
        # First we need to organize all the text into lines

        for text_node in self.text_nodes:

            if len(self.lines) == 0:
                self.lines.append(Line([text_node]))

            else:
                line = self.lines[-1]
                if line.includes(text_node):
                    line.add_node(text_node)
                else:
                    line.text_nodes = sorted(line.text_nodes, key=lambda node: node.get_x())
                    self.lines[-1] = line
                    new_line = Line([text_node])
                    self.lines.append(new_line)

    def as_string(self):
        s = ""
        for line in self.lines:
            s += line.as_string() + " "

        return s.strip()

    def get_x(self):
        if len(self.lines) > 0 and len(self.lines[0].words):
            return self.lines[0].words[0].get_x()
        elif self.features.image_node:
            return self.features.image_node.get_x()
        else:
            return None

    def get_y(self):
        if len(self.lines) > 0 and len(self.lines[0].words):
            return self.lines[0].words[0].get_y()
        elif self.features.image_node:
            return self.features.image_node.get_y()
        else:
            return None

    def get_width(self):
        if len(self.lines) > 0 and len(self.lines[0].words):
            return self.lines[0].words[0].get_x() - self.lines[0].words[-1].get_x() \
                   + self.lines[0].words[-1].get_width()
        elif self.features.image_node:
            return self.features.image_node.get_width()
        else:
            return None

    def get_height(self):
        if len(self.lines) > 0 and len(self.lines[0].words) > 0 and len(self.lines[-1].words):
            return self.lines[-1].words[0].get_y() - self.lines[0].words[0].get_y() \
                   + self.lines[-1].words[0].get_height()
        elif self.features.image_node:
            return self.features.image_node.get_height()
        else:
            return None


class NodeStatistics:
    """
    A set of statistics for a content area used for determining how to group and then
    annotate text with labels
    """

    def __init__(self, nodes):
        # Let's get some statistics to work with

        # Sort all the text nodes by y and group height first to understand where we believe
        # we have characters on the same line

        # Then we need to sort by X and work out where we have breaks between words
        x1s = [node.get_x() for node in nodes if node.get_x()]
        ys = [node.get_y() for node in nodes if node.get_y()]
        widths = [node.get_width() for node in nodes if node.get_width()]
        heights = [node.get_height() for node in nodes if node.get_height()] # this is font size
        x2s = [x + w for x,w in zip(x1s, widths)]
        char_spaces = [x1 - x2 for x1, x2 in zip(x1s[1:], x2s)]
        char_spaces = [s for s in char_spaces if s > 0.0]

        line_space_heights = []
        for idx in range(0, len(nodes)-1):
            curr_node = nodes[idx]
            next_node = nodes[idx + 1]
            if curr_node.get_y() and next_node.get_y():
                line_space_heights.append(abs(curr_node.get_y() - next_node.get_y()))

        # Get mean and standard deviation from the given data
        # Remove outliers by only getting the data within 1 standard deviation
        # Get the mean again

        self.updated_mean_space_width = 0.0
        self.updated_mean_width = 0.0
        self.updated_mean_height = 0.0
        self.updated_mean_line_space_height = 0.0

        if len(widths) > 0 and len(heights) > 0:
            self.mean_y = np.mean(ys)
            self.mean_width = np.mean(widths)
            self.mean_height = np.mean(heights)
            stdev_width = np.std(widths)
            stdev_height = np.std(heights)

            updated_widths = [w for w in widths if
                              ((w >= self.mean_width - stdev_width) and (w <= self.mean_width + stdev_width))]
            updated_heights = [h for h in heights if (
                        (h >= self.mean_height - stdev_height) and (h <= self.mean_height + stdev_height))]

            self.updated_mean_width = np.mean(updated_widths)
            self.updated_mean_height = np.mean(updated_heights)

        if len(line_space_heights):
            self.mean_line_space_height = np.mean(line_space_heights)
            updated_line_space_heights = [h for h in line_space_heights if h >= self.updated_mean_height * 0.75]
            self.updated_mean_line_space_height = min(updated_line_space_heights) \
                if len(updated_line_space_heights) > 0 else 0.0

        self.updated_mean_space_width = np.mean(char_spaces) if len(char_spaces) > 0 else 0.0

