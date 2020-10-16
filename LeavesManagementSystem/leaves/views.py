from braces.views import PermissionRequiredMixin
from django import forms
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, UpdateView, CreateView, DetailView

from .models import Leave, ApplierApprover


class LeaveRequests(PermissionRequiredMixin, ListView):
    template_name = 'leaves/requests.html'
    context_object_name = 'leave_requests'
    permission_required = 'leaves.view_leave_requests'
    raise_exception=True
    paginate_by = 8

    def get_queryset(self):
        """
        Get all pending-leaves with current logged-in user as approver
        """

        return Leave.objects.filter(approver=self.request.user).filter(status=Leave.PENDING).order_by('-date_applied').all()

class AppliedLeaves(PermissionRequiredMixin, ListView):
    template_name = 'leaves/applied-leaves-list.html'
    context_object_name = 'leave_requests'
    permission_required = 'leaves.request_leave'
    raise_exception=True
    paginate_by = 8

    def get_queryset(self):
        """
        Get all leaves with current logged-in user as applier 
        """
        
        return Leave.objects.filter(applier=self.request.user).order_by('-date_applied').all()

class LeaveRequestUpdate(PermissionRequiredMixin, UpdateView):
    model = Leave
    template_name = 'leaves/request-response.html'
    permission_required = 'leaves.approve_reject_leave'
    raise_exception=True
    fields = ['rejection_reason', 'status']
    labels = {
        'user': 'Applier',
        'rejection_reason': 'Rejection Reason'
    }

    def get_success_url(self):
        """
        Returns path-name for url-redirection on successfull updation with success message
        """

        messages.success(self.request, 'Response saved successfully!')
        return reverse('leave-requests')
    
    def get_context_data(self, **kwargs):
        """
        Extend context with applier and reason

        "**kwargs"
        """

        context = super(LeaveRequestUpdate, self).get_context_data(**kwargs)
        leave_request = self.get_object()
        
        context['applier'] = leave_request.applier
        context['reason'] = leave_request.reason

        return context

    def get_object(self, *args, **kwargs):
        """
        Returns leave-object if current logged-in user is the approver of it else raise permission-denied exception

        :*args:
        :**kwargs:
        """

        leave_request = super(LeaveRequestUpdate, self).get_object(*args, **kwargs)

        if self.request.user == leave_request.approver:
            return leave_request
        raise PermissionDenied() #or Http404

    def form_valid(self, form):
        """
        Check if status is REJECTED then Rejection-Reason must be provided

        :form:
        """
        status = form.cleaned_data['status']
        rejection_reason = form.cleaned_data['rejection_reason']

        if (status == Leave.REJECTED and not(rejection_reason)):
            messages.warning(self.request, "Rejection reason not mentioned")
            return super(LeaveRequestUpdate, self).form_invalid(form)

        self.object = form.save()
        return super().form_valid(form)

class LeaveRequestCreate(PermissionRequiredMixin, CreateView):
    model = Leave
    template_name = 'leaves/create-leave.html'
    permission_required = 'leaves.request_leave'
    raise_exception=True
    fields = ['date', 'reason']

    def get_success_url(self):
        """
        Returns path for url-redirection on successfull leave apply with Success Message
        """

        messages.success(self.request, 'Succesfully applied for leave!')
        return reverse('applied-leaves-list')
    
    def get_context_data(self, **kwargs):
        """
        Extend context with leave-approver

        "**kwargs"
        """
        
        context = super(LeaveRequestCreate, self).get_context_data(**kwargs)
        context['approver'] = ApplierApprover.objects.filter(user=self.request.user).first().approver
        return context

    def get_form(self):
        """
        Add date picker in form
        """
        
        form = super(LeaveRequestCreate, self).get_form()
        form.fields['date'].widget = forms.widgets.SelectDateWidget()
        return form

    def form_valid(self, form):
        """
        Add applier & approver to form-instance before validation check
        Try-Except IntegrityError for duplicate leaves of current user and return with error-message on exception

        :form:
        """

        form.instance.applier = self.request.user
        form.instance.approver = ApplierApprover.objects.filter(user=self.request.user).first().approver
        try:
            return super().form_valid(form)
        except IntegrityError as e:
            messages.warning(self.request, f'Already applied for {form.cleaned_data["date"]: "%B %d, %Y"}')
            return render(self.request, self.template_name, {'form': form, 'approver': ApplierApprover.objects.filter(user=self.request.user).first().approver})

class AppliedLeaveHistory(PermissionRequiredMixin, ListView):
    template_name = 'leaves/applied-leave-history-calendar.html'
    context_object_name = 'leaves'
    permission_required = 'leaves.request_leave'
    raise_exception=True

    def get_queryset(self):
        """ 
        Get all leaves with current logged-in user as applier
        """

        return Leave.objects.filter(applier=self.request.user).all()

class AppliersLeaveHistory(PermissionRequiredMixin, ListView):
    template_name = 'leaves/leaves-history-calendar.html'
    context_object_name = 'users'
    permission_required = 'leaves.view_appliers_leaves_history'
    raise_exception=True

    def get_queryset(self):
        """ 
        get all users' username with current logged-in user as approver
        """

        curr_user_applier_approver = ApplierApprover.objects.filter(approver=self.request.user).all()
        return User.objects.filter(applier__in=curr_user_applier_approver).values('username')

    def get_context_data(self, **kwargs):
        """
        Extend context with ajax-url for leave details request

        :kwargs:
        """

        context = super(AppliersLeaveHistory, self).get_context_data(**kwargs)
        context['leave_detail_ajax_url'] = reverse('applier-leaves-details', args=[123])
        return context
    
class ApplierLeavesDetails(PermissionRequiredMixin, DetailView):
    template_name = 'leaves/approvers-leaves-summary.html'
    permission_required = 'leaves.view_appliers_leaves_history'
    raise_exception=True

    def get(self, request, *args, **kwargs):
        """
        Gets Leaves detail for requested user in JSON after validation check

        :request:
        :args:
        :kwargs:
        """

        applier_username = kwargs.get('pk').lower()
        applier = User.objects.annotate(username_lower=Lower('username')).filter(username_lower=applier_username).first()
        
        if not(applier):
            response = JsonResponse({"error": "Invalid username!"})
            response.status_code = 404
            return response

        if request.is_ajax():
            if ApplierApprover.objects.filter(approver=self.request.user, user_id=applier).exists():
                leaves = Leave.objects.filter(applier=applier).all()
                srl = serializers.serialize('json',leaves)
                return HttpResponse(srl, content_type='application/json')
            else:
                response = JsonResponse({"error": "Unauthorized to view!"})
                response.status_code = 401
                return response

class LeavesHistory(PermissionRequiredMixin, ListView):
    template_name = 'leaves/leaves-history-calendar.html'
    context_object_name = 'users'
    permission_required = 'leaves.view_all_leaves_history'
    raise_exception = True

    def get_queryset(self):
        """ 
        get all user's usernames
        """

        return User.objects.values('username').all()
    
    def get_context_data(self, **kwargs):
        """
        Extend context with ajax-url for leave details request

        :kwargs:
        """

        context = super(LeavesHistory, self).get_context_data(**kwargs)
        context['leave_detail_ajax_url'] = reverse('user-leaves-details', args=[123])
        return context
    
class UserLeavesDetails(PermissionRequiredMixin, DetailView):
    permission_required = 'leaves.view_all_leaves_history'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Gets Leaves detail for requested user in JSON after validation check

        :request:
        :args:
        :kwargs:
        """

        applier_username = kwargs.get('pk').lower()
        applier = User.objects.annotate(username_lower=Lower('username')).filter(username_lower=applier_username).first()

        if not(applier):
            response = JsonResponse({"error": "Invalid username!"})
            response.status_code = 404
            return response

        if request.is_ajax():
            leaves = Leave.objects.filter(applier=applier).all()
            srl = serializers.serialize('json',leaves, fields=('status', 'date', 'reason', 'rejection_reason'))
            return HttpResponse(srl, content_type='application/json')
