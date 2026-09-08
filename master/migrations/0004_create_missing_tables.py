from django.db import migrations, transaction


# These models were `managed = False` when their original CreateModel migrations
# ran, so Django skipped the actual CREATE TABLE for them (Options.can_migrate()
# returns False for unmanaged models). Flipping them to managed = True and running
# makemigrations only recorded an options change (no-op on the DB) - the tables
# were never created. This migration creates whichever of them are still missing.
MODELS_TO_ENSURE = [
    ('tools', 'NomineeRelation'),
    ('tools', 'ClientTypeGender'),
    ('tools', 'RegistrationAuthority'),
    ('tools', 'SystemDay'),
    ('tools', 'Nationality'),
    ('tools', 'LegalStatus'),
    ('tools', 'DocumentType'),
    ('tools', 'LoanPurpose'),
    ('tools', 'Education'),
    ('tools', 'Salutation'),
    ('tools', 'LeadSource'),
    ('tools', 'LoanType'),
    ('tools', 'LoanPaymentScheme'),
    ('master', 'ContactMaster'),
    ('master', 'ClientMaster'),
    ('crm', 'LeadQuotation'),
    ('crm', 'LeadQuotationDocuments'),
    ('loan', 'RequestWorkflow'),
    ('loan', 'RoleTransactionLimit'),
    ('loan', 'LoanRequest'),
    ('loan', 'LoanRequestHistory'),
    ('loan', 'LoanLedger'),
]


def create_missing_tables(apps, schema_editor):
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    pending = []
    for app_label, model_name in MODELS_TO_ENSURE:
        model = apps.get_model(app_label, model_name)
        if model._meta.db_table not in existing_tables:
            pending.append(model)

    # Create in dependency order automatically: keep looping over whatever is
    # still pending, creating what we can (FK targets already exist) and
    # retrying the rest, until nothing more can be created.
    while pending:
        still_pending = []
        progressed = False
        for model in pending:
            try:
                with transaction.atomic(using=connection.alias):
                    schema_editor.create_model(model)
            except Exception:
                still_pending.append(model)
            else:
                existing_tables.add(model._meta.db_table)
                progressed = True
        if not progressed:
            raise RuntimeError(
                "Could not create tables for: "
                + ", ".join(m._meta.db_table for m in still_pending)
            )
        pending = still_pending


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0003_alter_clientmaster_options_and_more'),
        ('tools', '0003_alter_clienttypegender_options_and_more'),
        ('crm', '0002_alter_leadquotation_options_and_more'),
        ('loan', '0002_alter_loanledger_options_alter_loanrequest_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_tables, noop),
    ]
