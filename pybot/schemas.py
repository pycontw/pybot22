import enum


class BaseEnum(enum.Enum):
    # Provide the ability to compare with str
    def __eq__(self, tar):
        if isinstance(tar, str):
            return self.value == tar
        return self == tar


class QuestionType(BaseEnum):
    TEXT = 'text'
    SELECTION = 'selection'  # Will show the full text of every option.
    OPTION_ONLY = 'option_only'  # Will only show A, B, C, and D.
    QUESTIONARE= 'questionare'
    PURE_MESSAGE = 'pure_message'
    SERVICE = 'service'
