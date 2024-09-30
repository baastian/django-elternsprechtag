from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from ..views.students import *

urlpatterns = [
    ## Students ##
    path("", StudentListView.as_view(), name="student_list_view"),
    path("<pk>/view", StudentDetailView.as_view(), name="student_details_view"),
    path("<pk>/edit", StudentEdit.as_view(), name="student_edit_view"),
    path(
        "<pk>/reset_relationship",
        ResetStudentParentRelationshipView.as_view(),
        name="student_reset_relationship_view",
    ),
    path(
        "<pk>/send_registration_mail",
        UpcommingUserSendRegistrationMail.as_view(),
        name="administrative_student_send_registration_mail",
    ),
    path(
        "<pk>/parent/create",
        ManualParentRegistration.as_view(),
        name="administrative_student_register_parent",
    ),
    path(
        "<pk>/parent/add",
        ManualParentAddStudent.as_view(),
        name="administrative_student_parent_add_student",
    ),
    path(
        "import/upload/",
        StudentImportStart.as_view(),
        name="student_import_filepload",
    ),
    path(
        "import/view/",
        StudentImportListChanges.as_view(),
        name="student_import_listchanges",
    ),
    path(
        "import/all/apply/",
        StudentImportApproveAndApplyAll.as_view(),
        name="student_import_apply_all_changes",
    ),
    path(
        "import/<pk>/apply/",
        StudentImportApproveAndApply.as_view(),
        name="student_import_apply_change",
    ),
    path(
        "import/all/cancel/",
        StudentImportCancel.as_view(),
        name="student_import_cancel",
    ),
    path(
        "import/<pk>/cancel/",
        StudentImportRemoveEntry.as_view(),
        name="student_import_remove_entry",
    ),
    path(
        "import/<pk>/edit/",
        StudentChangeEditView.as_view(),
        name="student_import_edit",
    ),
    path(
        "import/apply/operation/<int:operation>/",
        StudentImportApproveAndApplyWithOperation.as_view(),
        name="student_import_apply_with_operation",
    ),
    path(
        "upcomming_user/batch_send/",
        UpcommingUserBatchSendView.as_view(),
        name="student_upcomming_user_batch_send",
    ),
]
