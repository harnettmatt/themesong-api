from copy import deepcopy

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Persistable(Base):
    __abstract__ = True

    def __eq__(self, other):
        classes_match = isinstance(other, self.__class__)
        self_dict, other_dict = deepcopy(self.__dict__), deepcopy(other.__dict__)
        # ignore SQLAlchemy internal stuff
        self_dict.pop("_sa_instance_state", None)
        other_dict.pop("_sa_instance_state", None)
        attrs_match = self_dict == other_dict

        return classes_match and attrs_match

    def __ne__(self, other):
        return not self.__eq__(other)
