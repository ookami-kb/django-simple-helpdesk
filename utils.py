from helpdesk.utils import DefaultProfile


class HelpdeskDefaultProfile(DefaultProfile):
    @property
    def label(self):
        return self.user.email
