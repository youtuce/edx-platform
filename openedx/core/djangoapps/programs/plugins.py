import logging

from django.template.loader import render_to_string
from django.utils.translation import ugettext_noop as _

from openedx.core.lib.studio_entities import StudioEntity


logger = logging.getLogger(__name__)


class ProgramsEntity(StudioEntity):
    """Studio entity for administering Programs (e.g., XSeries)."""
    tab_text = _('Programs')
    button_text = _('New Program')
    # TODO (RFL): List *template*, not view. A view would work better if the plugin
    # was responsible for rendering the whole page.
    list_view = render_to_string('programs/list.html')
    create_view = render_to_string('programs/create.html')

    @classmethod
    def is_enabled(cls, user=None):
        # TODO (RFL): Read a feature flag and verify the user has permission to administer Programs.
        return True
