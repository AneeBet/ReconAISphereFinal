from app.models.bank import Bank
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.repositories.seed_users_repository import SeedUsersRepository
from app.utils.password import hash_password


class SeedUsersService:

    def __init__(self, repository: SeedUsersRepository):
        self.repository = repository

    def seed(self):

        organization = self.repository.get_organization()

        if organization is None:

            organization = Organization(
                name="ReconSphere",
                country="India",
                timezone="Asia/Kolkata",
                currency="INR"
            )

            organization = self.repository.create_organization(organization)

        users = [

            ("System","Administrator","admin@reconsphere.ai",UserRole.ADMIN),

            ("Operations","User","ops@reconsphere.ai",UserRole.OPS),

            ("Audit","User","audit@reconsphere.ai",UserRole.AUDITOR),

            ("Viewer","User","viewer@reconsphere.ai",UserRole.VIEWER)

        ]

        created = []

        for first,last,email,role in users:

            if self.repository.get_user(email):
                continue

            self.repository.create_user(

                User(

                    organization_id=organization.id,

                    first_name=first,

                    last_name=last,

                    email=email,

                    password_hash=hash_password("Recon@123"),

                    role=role,

                    is_active=True

                )

            )

            created.append(email)

        banks = [
            ("Global Bank A", "GLBAINBBXXX", "India", "INR"),
            ("Overseas Bank B", "OVBBUS33XXX", "United States", "USD"),
        ]

        seeded_banks = []

        for bank_name, bic, country, currency in banks:

            if self.repository.get_bank(bic):
                continue

            bank = self.repository.create_bank(
                Bank(
                    organization_id=organization.id,
                    bank_name=bank_name,
                    bic_swift=bic,
                    country=country,
                    currency=currency,
                    is_active=True
                )
            )

            seeded_banks.append(
                {"id": str(bank.id), "bank_name": bank.bank_name, "bic": bic}
            )

        return {
            "organization": organization.name,
            "created": created,
            "banks": seeded_banks,
            "password": "Recon@123"
        }
