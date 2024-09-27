from django.db import models

# Create your models here.

class Groups(models.Model):
    # GroupId=models.CharField(max_length=20,primary_key=True)
    Name=models.CharField(max_length=30)
    Limit=models.PositiveIntegerField(default=2)
    Password=models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.Name


class Member(models.Model):
    Name=models.CharField(max_length=100)
    Group=models.ForeignKey(Groups,on_delete=models.CASCADE)
    Role=models.CharField(max_length=10,default="member")
    ReportCount=models.PositiveIntegerField(default=0)
    isOnline=models.BooleanField(default=True)
    

    def __str__(self) -> str:
        return self.Name
    
class Report(models.Model):
    reported_member = models.ForeignKey(Member, related_name='reports', on_delete=models.CASCADE)
    reported_by = models.ForeignKey(Member, related_name='reported', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('reported_member', 'reported_by')

    def __str__(self):
        return f'{self.reported_by} reported {self.reported_member}'
    




