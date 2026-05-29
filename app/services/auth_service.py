import bcrypt


class AuthService:
    def hash_password(self, password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )
        return hashed_password.decode("utf-8")

    def verify_password(
            self,
            plain_password: str,
            hashed_password: str
    ) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

