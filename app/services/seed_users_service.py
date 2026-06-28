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

        return {
            "organization": organization.name,
            "created": created,
            "password": "Recon@123"
        }
