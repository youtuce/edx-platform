"""
Base class for pages in courseware.
"""

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
from . import BASE_URL
from .tab_nav import TabNavPage


class CoursePage(PageObject):
    """
    Abstract base class for page objects within a course.
    """

    # Overridden by subclasses to provide the relative path within the course
    # Paths should not include the leading forward slash.
    url_path = ""

    def __init__(self, browser, course_id):
        """
        Course ID is currently of the form "edx/999/2013_Spring"
        but this format could change.
        """
        super(CoursePage, self).__init__(browser)
        self.course_id = course_id

    @property
    def url(self):
        """
        Construct a URL to the page within the course.
        """
        return BASE_URL + "/courses/" + self.course_id + "/" + self.url_path

    def has_tab(self, tab_name):
        """
        Returns true if the current page is showing a tab with the given name.
        :return:
        """
        tab_nav = TabNavPage(self.browser)
        return tab_name in tab_nav.tab_names

    def verify_skip_to_container_exists(self):
        """
        Checks to make sure a container with an ID that matches
        the skip link a href is present.
        """
        skip_to = self.q(css=".nav-skip").attrs('href')[0]
        skip_href = skip_to.split('/')[-1]
        return EmptyPromise(
            self.q(css=skip_href).is_present, "Main content area is present"
        ).fulfill()

    # def skip_to_main_content(self):
    #     """
    #     Checks to make sure the skip link skips to its href
    #     and the container receives focus.
    #     """
    #     skip_to = self.q(css=".nav-skip").attrs('href')[0]
    #     skip_href = skip_to.split('/')[-1]
    #     self.q(css=skip_href).click
    #     self.wait_for(
    #         self.q(css=skip_href).is_focused, "Main content area is focusable'"
    #     )
