from util import get_html_page


class LinkHolderOpenJDK:
    def __init__(self, version, operation_system, architecture, link):
        self.so = operation_system.lower()
        self.architecture = architecture
        self.version = version
        self.link = link

    def __str__(self):
        return f"{self.version} {self.so} {self.architecture}"


class OpenJDKExtractor:

    def __init__(self):
        self.__open_jdk_archive = "https://jdk.java.net/archive/"
        self.__holder = []
        self.__get_link()

    def __get_link(self):
        soup = get_html_page(self.__open_jdk_archive)
        current_version = None
        for i in soup.find_all("tr"):
            test = i.find_all("th")
            if len(test) == 0:
                continue
            if len(test) == 1:
                current_version = test[0].text
                continue
            self.__holder.append(LinkHolderOpenJDK(current_version, test[0].text, test[1].text, i.a['href']))

    def get_links_linux(self):
        return [holder for holder in self.__holder if "linux" in holder.so]

    def get_links_windows(self):
        return [holder for holder in self.__holder if "windows" in holder.so]


class MavenExtractor:

    @staticmethod
    def get_versions():
        url_maven = "http://archive.apache.org/dist/maven/maven-3/"
        soup = get_html_page(url_maven)
        versions = {}
        for a in soup.find_all("a"):
            if "/" in a.text:
                version = a.text.replace("/", "")
                versions[
                    version] = f"http://archive.apache.org/dist/maven/maven-3/{version}/binaries/apache-maven-{version}-bin.tar.gz"
        return versions



