import pathlib
import os


class Writer:
    def article_path(self, date, basename):
        article_path_fmt = "posts/{}/{}.ja.md"
        date_fmt = "%Y.%m"  # TODO:
        path = article_path_fmt.format(
            date.strftime(date_fmt), basename)
        return path

    def create_article_path(self, base_path, date, basename):
        article_path = self.article_path(date, basename)
        abs_article_path = os.path.join(base_path, article_path)
        parent_path = os.path.join(
            base_path, os.path.dirname(abs_article_path))
        pathlib.Path(parent_path).mkdir(parents=True, exist_ok=True)
        return abs_article_path

    def write_md(self, article_path, md):
        # TODO: tags, categories
        content = []
        content.append("---")
        content.append("title: {}".format(md["title"]))
        content.append("date: {}".format(md["date"]))
        content.append("---")
        content.append("\n\n<!-- more -->\n\n".join(md["body"]))
        with open(article_path, "w") as out:
            out.write("\n".join(content))
        print("💾 wrote out to: {}".format(article_path))

    def write(self, base_path, article):
        md = {
            "title": None,
            "date": None,
            "tags": [],
            "body": (None, None)
        }
        date = None
        basename = None

        for attr in article.attributes:
            if attr.name() == "Title":
                md["title"] = attr.value()
            if attr.name() == "Date":
                md["date"] = attr.value()
                date = attr.value()
            if attr.name() == "Basename":
                basename = attr.value()
            if attr.name() == "Body":
                md["body"] = (attr.value(), md["body"][1])
            if attr.name() == "ExtendedBody":
                md["body"] = (md["body"][0], attr.value())

        article_path = self.create_article_path(base_path, date, basename)
        self.write_md(article_path, md)
