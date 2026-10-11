"""Prepare Django's schema during deployment; static assets are collected by Vercel."""
import os
from django.core.management import call_command


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qorgo.settings')
    # Migrations use a direct connection when the database provider supplies one.
    direct_url = os.getenv('DATABASE_URL_UNPOOLED') or os.getenv('POSTGRES_URL_NON_POOLING')
    if direct_url:
        os.environ['DATABASE_URL'] = direct_url
    import django
    django.setup()
    # Reject model changes whose migration files were not committed.
    call_command('makemigrations', check=True, dry_run=True, interactive=False)
    call_command('migrate', interactive=False)
    if os.getenv('VERCEL_ENV') == 'production' and os.getenv('BOOTSTRAP_ADMIN_PASSWORD'):
        call_command('bootstrap_admin')


if __name__ == '__main__':
    main()
