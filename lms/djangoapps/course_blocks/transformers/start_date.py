"""
...
"""
from openedx.core.lib.block_cache.transformer import BlockStructureTransformer
from courseware.access_utils import check_start_date
from xmodule.course_metadata_utils import DEFAULT_START_DATE

from .utils import get_field_on_block


class StartDateTransformer(BlockStructureTransformer):
    """
    ...
    """
    VERSION = 1
    MERGED_START_DATE = 'merged_start_date'

    @classmethod
    def get_merged_start_date(cls, block_structure, block_key):
        """
        ...
        """
        return block_structure.get_transformer_block_data(
            block_key, cls, cls.MERGED_START_DATE, False
        )

    @classmethod
    def collect(cls, block_structure):
        """
        Collects any information that's necessary to execute this transformer's
        transform method.
        """
        block_structure.request_xblock_fields('days_early_for_beta')

        for block_key in block_structure.topological_traversal():

            # compute merged value of start date from all parents
            parents = block_structure.get_parents(block_key)
            min_all_parents_start_date = min(
                cls.get_merged_start_date(block_structure, parent_key)
                for parent_key in parents
            ) if parents else None

            # set the merged value for this block
            block_start = get_field_on_block(block_structure.get_xblock(block_key), 'start')
            if min_all_parents_start_date is None:
                # no parents so just use value on block or default
                merged_start_value = block_start or DEFAULT_START_DATE
            elif not block_start:
                # no value on this block so take value from parents
                merged_start_value = min_all_parents_start_date
            else:
                # max of merged-start-from-all-parents and this block
                merged_start_value = max(min_all_parents_start_date, block_start)
            block_structure.set_transformer_block_data(
                block_key,
                cls,
                cls.MERGED_START_DATE,
                merged_start_value
            )

    def transform(self, user_info, block_structure):
        """
        Mutates block_structure based on the given user_info.
        """
        if user_info.has_staff_access:
            return

        block_structure.remove_block_if(
            lambda block_key: not check_start_date(
                user_info.user,
                block_structure.get_xblock_field(block_key, 'days_early_for_beta'),
                self.get_merged_start_date(block_structure, block_key),
                user_info.course_key,
            )
        )
