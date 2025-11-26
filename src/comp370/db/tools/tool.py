from sqlalchemy.orm import Session


class Tool:
    def __init__(self, session: Session):
        self.session = session
