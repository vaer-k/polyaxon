import logging

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from jobs.statuses import JobLifeCycle
from libs.decorators import ignore_raw, ignore_updates, ignore_updates_pre
from plugins.models import NotebookJob, NotebookJobStatus, TensorboardJob, TensorboardJobStatus
from projects.models import Project
from repos.utils import assign_code_reference
from runner.schedulers import notebook_scheduler, tensorboard_scheduler

logger = logging.getLogger('polyaxon.plugins')


@receiver(pre_save, sender=TensorboardJob, dispatch_uid="tensorboard_job_saved")
@ignore_updates_pre
@ignore_raw
def add_tensorboard_code_reference(sender, **kwargs):
    assign_code_reference(kwargs['instance'])


@receiver(post_save, sender=TensorboardJob, dispatch_uid="tensorboard_job_saved")
@ignore_updates
@ignore_raw
def new_tensorboard_job(sender, **kwargs):
    instance = kwargs['instance']
    instance.set_status(status=JobLifeCycle.CREATED)


@receiver(pre_save, sender=NotebookJob, dispatch_uid="notebook_job_saved")
@ignore_updates_pre
@ignore_raw
def add_notebook_code_reference(sender, **kwargs):
    assign_code_reference(kwargs['instance'])


@receiver(post_save, sender=NotebookJob, dispatch_uid="notebook_job_saved")
@ignore_updates
@ignore_raw
def new_notebook_job(sender, **kwargs):
    instance = kwargs['instance']
    instance.set_status(status=JobLifeCycle.CREATED)


@receiver(post_save, sender=TensorboardJobStatus, dispatch_uid="new_tensorboard_job_status_saved")
@ignore_updates
@ignore_raw
def new_tensorboard_job_status(sender, **kwargs):
    instance = kwargs['instance']
    job = instance.job
    # Update job last_status
    job.job_status = instance
    job.save()


@receiver(post_save, sender=NotebookJobStatus, dispatch_uid="new_notebook_job_status_saved")
@ignore_updates
@ignore_raw
def new_notebook_job_status(sender, **kwargs):
    instance = kwargs['instance']
    job = instance.job
    # Update job last_status
    job.job_status = instance
    job.save()


@receiver(pre_delete, sender=Project, dispatch_uid="project_stop_plugins")
@ignore_raw
def project_stop_plugins(sender, **kwargs):
    instance = kwargs['instance']
    tensorboard_scheduler.stop_tensorboard(instance, update_status=False)
    notebook_scheduler.stop_notebook(instance, update_status=False)
