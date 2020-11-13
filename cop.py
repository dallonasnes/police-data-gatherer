class Cop():
    def __init__(self, name, role, total_payments, page_url, is_active=False):
        self.name: str = name
        self.role: str = role
        self.total_payments: str = total_payments
        self.page_url: str = page_url #detailed page for individual cop, projects.chicagoreporter.com
        self.complaint_count: int = None
        self.is_active = is_active

    def set_is_active(self, is_active):
        self.is_active = is_active

    def set_complaint_count(self, complaint_count):
        self.complaint_count = complaint_count

    def has_complaint_count(self):
        return self.complaint_count is not None
    
    def __str__(self):
        return self.name + ' - ' + self.role + ' - ' + self.is_active + ' - ' + self.total_payments + ' - ' + str(self.complaint_count) + ' - detailed URL: ' + self.page_url
    
    def get_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'total_payments': self.total_payments,
            'page_url': self.page_url,
            'complaint_count': self.complaint_count,
            'is_active': self.is_active
        }
