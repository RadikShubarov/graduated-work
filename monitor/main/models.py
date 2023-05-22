from django.db import models


# Create your models here.
class Host(models.Model):
    host = models.CharField(max_length=80)

    def __str__(self):
        return self.host


class SarData(models.Model):
    log_time = models.CharField('log_time', max_length=50)
    time = models.CharField('timeStamp', max_length=50)
    user = models.DecimalField('user', max_digits=6, decimal_places=2)
    nice = models.DecimalField('nice', max_digits=6, decimal_places=2)
    system = models.DecimalField('system', max_digits=6, decimal_places=2)
    iowait = models.DecimalField('iowait', max_digits=6, decimal_places=2)
    steal = models.DecimalField('steal', max_digits=6, decimal_places=2)
    host_machine = models.ForeignKey('Host', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.log_time} {self.time} {self.user} {self.nice} {self.system} {self.iowait} {self.steal} ' \
               f'{self.host_machine}'


class PcaPeaks(models.Model):
    peak = models.DecimalField('peak', max_digits=6, decimal_places=2)
    host_owner = models.ForeignKey('Host', on_delete=models.PROTECT, null=True)
    log_times = models.CharField('log_time', max_length=50, null=True)
    danger_prediction = models.BooleanField('predict', null=True)

    def __str__(self):
        return f'{self.peak} {self.host_owner} {self.log_times} {self.danger_prediction} '
