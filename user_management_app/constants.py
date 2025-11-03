ROLE_CHOICES = [
    ('user', 'User'),
    ('designer', 'Designer'),
    ('developer', 'Developer'),
    ('customizer', 'Customizer'),
    ('admin', 'Admin'),
]
USER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

MEMBERSHIP_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('active', 'Active'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
]

MEMBERSHIP_TYPE_CHOICES = [
    ('individual', 'Individual'),
    ('team', 'Team'),
    ('organization', 'Organization'),
    ('enterprise', 'Enterprise'),
]

INTEREST_CHOICES = [
    ('football', 'Football'),
    ('basketball', 'Basketball'),
    ('hockey', 'Hockey'),
    ('baseball', 'Baseball'),
    ('soccer', 'Soccer'),
    ('custom', 'Custom'),
]