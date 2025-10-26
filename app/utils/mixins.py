from datetime import datetime

from sqlalchemy import DateTime, event, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped


class TimestampMixin:

    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)


class ModifiedMixin(TimestampMixin):
    """The __exclude__ type must be `set` type.

    Example:
        __exclude__ = {'title'}
    """

    __exclude__ = set()

    modified_at: Mapped[datetime] = Column(DateTime, nullable=True)

    @property
    def last_modification_time(self):
        return self.modified_at or self.created_at

    @staticmethod
    def before_update(mapper, connection, target):
        if not target.object.__exclude__.issubset(target.unmodified):
            return

        target.object.modified_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update, raw=True)


class ActivationMixin:
    activated_at: Mapped[datetime] = Column(DateTime, nullable=True)

    @hybrid_property
    def is_active(self):
        return self.activated_at is not None

    @is_active.setter
    def is_active(self, value):
        self.activated_at = datetime.utcnow() if value else None

    @is_active.expression
    def is_active(self):
        return self.activated_at.isnot(None)

    @classmethod
    def filter_activated(cls, query):
        return query.filter(cls.is_active)

    @classmethod
    def import_value(cls, column, v):
        if column.key == cls.is_active.key and not isinstance(v, bool):
            return str(v).lower() == 'true'
        return super().import_value(column, v)


class AutoActivationMixin(ActivationMixin):

    activated_at: Mapped[datetime] = Column(DateTime, nullable=True, default=datetime.utcnow)


class DeactivationMixin(ActivationMixin):

    deactivated_at: Mapped[datetime] = Column(DateTime, nullable=True)

    @ActivationMixin.is_active.setter
    def is_active(self, value):
        now = datetime.utcnow()
        if value:
            self.activated_at = now
            self.deactivated_at = None
        else:
            self.activated_at = None
            self.deactivated_at = now


class SoftDeleteMixin:
    removed_at: Mapped[datetime] = Column(DateTime, nullable=True)

    def assert_is_not_deleted(self):
        if self.is_deleted:
            raise ValueError('Object is already deleted.')

    def assert_is_deleted(self):
        if not self.is_deleted:
            raise ValueError('Object is not deleted.')

    @property
    def is_deleted(self):
        return self.removed_at is not None

    def soft_delete(self, ignore_errors=False):
        if not ignore_errors:
            self.assert_is_not_deleted()
        self.removed_at = datetime.utcnow()

    def soft_undelete(self, ignore_errors=False):
        if not ignore_errors:
            self.assert_is_deleted()
        self.removed_at = None

    @staticmethod
    def before_delete(mapper, connection, target):
        raise AssertionError(f'Cannot remove {target}')

    @classmethod
    def __declare_last__(cls):
        from sqlalchemy import event
        event.listen(cls, 'before_delete', cls.before_delete)

    @classmethod
    def filter_deleted(cls, query):
        return query.filter(cls.removed_at.isnot(None))

    @classmethod
    def exclude_deleted(cls, query):
        return query.filter(cls.removed_at.is_(None))

