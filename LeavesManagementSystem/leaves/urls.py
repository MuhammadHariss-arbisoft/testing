from django.urls import path
from .views import (LeaveRequests, LeaveRequestUpdate, AppliedLeaves,
                     LeaveRequestCreate, AppliedLeaveHistory, AppliersLeaveHistory,
                      ApplierLeavesDetails, UserLeavesDetails, LeavesHistory)

urlpatterns = [
    path('requests/', LeaveRequests.as_view(), name='leave-requests'),
    path('request/response/<pk>', LeaveRequestUpdate.as_view(), name='leave-request-response'),
    path('applied/', AppliedLeaves.as_view() , name='applied-leaves-list'),
    path('create/', LeaveRequestCreate.as_view(), name='leave-request-create'),
    path('summary/', AppliedLeaveHistory.as_view(), name='applied-leave-history'),
    path('history/', AppliersLeaveHistory.as_view(), name='appliers-leaves-history'),
    path('history/<pk>', ApplierLeavesDetails.as_view(), name='applier-leaves-details'),
    path('all/history/', LeavesHistory.as_view(), name='users-leaves-history'),
    path('all/history/<pk>', UserLeavesDetails.as_view(), name='user-leaves-details')
]
