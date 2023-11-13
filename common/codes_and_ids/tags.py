from enum import Enum


class OldImageTag(Enum):
    # TODO: Move to separate python module
    # # # Special tags (not used for XMP files)
    ALL = '∀ ALL'
    OTHER = '¬ OTHER'
    # # # Mandatory tags.
    # Each image should have one and only one tag.
    GOOD = '🟢 GOOD'
    BAD = '🔴 BAD'
    MOVE_TO_0 = '📁 MOVE_TO_0'
    REVIEW = '🔍 REVIEW'
    # # # Additional tags.
    # Each image may have one or more tags.
    NO_PACKAGE = '∅ NO_PACKAGE'
    OPEN_PACKAGE = '🛍️ OPEN_PACKAGE'
    SEMI_CLOSED_PACKAGE = '🛍️ SEMI_CLOSED_PACKAGE'
    FULLY_CLOSED_PACKAGE = '🛍️ FULLY_CLOSED_PACKAGE'
    PLATE = '🍽️ PLATE'
    BARCODE = '‖‖ BARCODE'
    MANUFACTURER_PACKAGE = '🏭 MANUFACTURER_PACKAGE'
    NET = '# NET'
    # # # Additional tags for testing purposes
    HAIRSTYLE = '🦱 HAIRSTYLE'
    ROSSMANN = '🐎 ROSSMANN'

    def __repr__(self):
        return f'<{self.name}>'


class ImageTag(Enum):
    # Special tags for usage in various rules
    ALL = 'ALL'
    OTHER = 'OTHER'
    NOTAG = 'NOTAG'
    # Package tags
    PKG_PLASTIC_BAG = 'PKG.PLASTIC.BAG'
    PKG_NET_BAG = 'PKG.NET.BAG'
    # Special tag for train/test separation
    TEST = 'TEST'

    def __repr__(self):
        return f'<{self.name}>'

    @property
    def emoji(self) -> str:
        return image_tag_emoji.get(self, image_tag_emoji[None])


image_tag_emoji = {
    None: '❓',
    ImageTag.NOTAG: '∅',
    ImageTag.TEST: '🖥',
    ImageTag.PKG_NET_BAG: '🕸',
    ImageTag.PKG_PLASTIC_BAG: '🛍'
}
