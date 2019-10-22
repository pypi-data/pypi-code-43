#!/home/dd/anaconda3/bin/python

class Hubby:
    """Pornhub Object."""
    
    def __init__(self, pornhub_hash, title=None, tags=[], bits=[], drips=[]):
        
        self.hash = pornhub_hash
        self.omm = "p." + pornhub_hash
        self.url = self.build_pornhub_url()
        if title:
            self.omm += "." + title.replace(" ","_")
            self.title = title
        else:
            self.title = ""
        if tags:
            for tag in tags:
                self.omm += "." + tag
            self.tags = tags

                
        self.html = self.build_html()
        
    def build_html(self):

        if self.tags:
            html_str = '<a href="' + str(self.url) + '" title="' + " ".join(self.tags) +  '">' + str(self.title) + '</a>'
        else:
            html_str = '<a href="' + str(self.url) + '">' + str(self.title) + '</a>'

        try: 
            for item in self.bits:        
                html_str += '  [' + item.html + ']'
        except:
            pass

#        if isinstance(self, Drip):
#            html_str +=  '  ' + '(a)'

        return html_str    
    
    
    
    def extract_pornhub_hash(pornhub_url):
        """Takes Pornhub URL, returns Pornhub hash."""

        m = re.search(r'viewkey=([a-z0-9]{15})$', pornhub_url)
        result = m.group(1)

        return result

    def build_pornhub_url(self):
        """Takes Pornhub Object string, returns Pornhub video URL."""
        
        url = "https://www.pornhub.com/view_video.php?viewkey=" + self.hash

        return url
    