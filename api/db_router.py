# settings.DATABASES defines 'default' and 'erp_db' as two separate aliases
# for the exact same physical Postgres database. Without this router,
# Django's ORM refuses to set a FK between model instances fetched through
# different aliases (e.g. `contact.created_by = request.user`, since
# request.user resolves via 'default' while views create master/tools/etc.
# records via `Model.objects.using(DB_NAME)` i.e. 'erp_db') even though both
# aliases ultimately point at the same rows.
SAME_DATABASE_ALIASES = {'default', 'erp_db'}


class SameDatabaseRouter:
    def allow_relation(self, obj1, obj2, **hints):
        if obj1._state.db in SAME_DATABASE_ALIASES and obj2._state.db in SAME_DATABASE_ALIASES:
            return True
        return None
