from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime

def date_validate(chosen_date):
    if chosen_date < datetime.date.today():
        raise ValidationError('Invalid Date: It must be atleast of today')
    return chosen_date

class Leave(models.Model):
    APPROVED = 'APPROVED'
    PENDING = 'PENDING'
    REJECTED = 'REJECTED'

    leave_choices = (
        (APPROVED,'APPROVED'),
        (PENDING, 'PENDING'),
        (REJECTED, 'REJECTED')
    )

    applier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applier_leaves', null=False)
    approver = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='approver_leaves', null=False)

    date = models.DateField(default=datetime.date.today, validators=[date_validate])
    date_applied = models.DateField(auto_now=True)

    reason = models.CharField(max_length=50, null=False, blank=False)
    rejection_reason = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=10, choices=leave_choices, default=PENDING, null=False)

    class Meta:
        unique_together = ('applier', 'date')
    
    # def clean(self):
    #     super().clean()
    #     if (self.status == self.REJECTED) and not(self.rejection_reason):
    #         raise ValidationError('*must specify rejection reason')



class ApplierApprover(models.Model):
    user = models.OneToOneField(User, related_name='applier', on_delete=models.CASCADE)
    approver = models.ForeignKey(User, related_name='appliers', on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return f'({self.user.username},{self.approver.username})'
