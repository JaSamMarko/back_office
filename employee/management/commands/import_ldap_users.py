import ldap
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from employee.models import Employee
from decouple import config

User = get_user_model()

class Command(BaseCommand):
    help = 'Import active users (except those with prefixes from settings)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--new-only',
            action='store_true',
            help='Import only new users (skip existing ones)'
        )

    def handle(self, *args, **options):
        # Prefixes to skip from settings
        skip_prefixes = config('LDAP_SKIP_PREFIXES', default='adm_,test_,temp_').split(',')
        skip_prefixes = [prefix.strip().lower() for prefix in skip_prefixes if prefix.strip()]
        
        self.stdout.write(f"Skipping prefixes: {skip_prefixes}")

        # Connect to LDAP
        try:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            
            conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            conn.protocol_version = ldap.VERSION3
            conn.simple_bind_s(
                settings.AUTH_LDAP_BIND_DN,
                settings.AUTH_LDAP_BIND_PASSWORD
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"ERROR connecting to LDAP: {e}"))
            return

        # Filter for active users
        search_filter = "(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
        attributes = ['sAMAccountName', 'givenName', 'sn']

        try:
            results = conn.search_s(
                settings.AUTH_LDAP_SEARCH_BASE,
                ldap.SCOPE_SUBTREE,
                search_filter,
                attributes
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"ERROR searching LDAP: {e}"))
            return
        finally:
            try:
                conn.unbind()
            except:
                pass

        # Process results
        new_users = 0
        new_employees = 0
        existing_users = 0
        skipped_users = 0

        for dn, entry in results:
            if not isinstance(entry, dict):
                continue

            try:
                # Decode attributes
                username = entry.get('sAMAccountName', [None])[0]
                if isinstance(username, bytes):
                    username = username.decode('utf-8')
                if not username:
                    continue

                # Check prefixes
                username_lower = username.lower()
                if any(username_lower.startswith(prefix) for prefix in skip_prefixes):
                    skipped_users += 1
                    self.stdout.write(f"SKIPPED (prefix): {username}")
                    continue

                first_name = entry.get('givenName', [None])[0]
                if isinstance(first_name, bytes):
                    first_name = first_name.decode('utf-8')

                last_name = entry.get('sn', [None])[0]
                if isinstance(last_name, bytes):
                    last_name = last_name.decode('utf-8')

                # Check existing user
                if options['new_only'] and User.objects.filter(username=username).exists():
                    existing_users += 1
                    continue

                # Create User
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first_name or '',
                        'last_name': last_name or '',
                    }
                )

                if created:
                    new_users += 1
                    self.stdout.write(self.style.SUCCESS(f"CREATED USER: {username}"))

                    # Create minimal Employee record
                    Employee.objects.create(
                        user=user,
                        first_name=first_name or '',
                        last_name=last_name or '',
                    )
                    new_employees += 1
                    self.stdout.write(self.style.SUCCESS(f"CREATED EMPLOYEE: {username}"))
                else:
                    self.stdout.write(f"EXISTING USER: {username}")

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"ERROR processing {username}: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(
            f"\nCompleted!\n"
            f"New users: {new_users}\n"
            f"New employees: {new_employees}\n"
            f"Existing users: {existing_users}\n"
            f"Skipped users: {skipped_users}"
        ))