from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from django.apps import apps
from .serializers import AssessmentSerializer, UserResponseSerializer

# Get models using string references to avoid circular imports
Assessment = apps.get_model('assessments', 'Assessment')
UserResponse = apps.get_model('assessments', 'UserResponse')

@login_required
def assessment_list(request):
    """
    View to display all active assessments.
    """
    assessments = Assessment.objects.filter(is_active=True)
    return render(request, 'assessments/assessment_list.html', {'assessments': assessments})

@login_required
def assessment_detail(request, pk):
    """
    View to display a single assessment and handle response submission.
    """
    assessment = get_object_or_404(Assessment, pk=pk)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text')
        # Create a new UserResponse object linked to the current user and assessment
        UserResponse.objects.create(user=request.user, assessment=assessment, text_response=response_text)
        return redirect('assessment_results', pk=assessment.pk)
    
    return render(request, 'assessments/assessment_detail.html', {'assessment': assessment})

@login_required
def assessment_results(request, pk):
    """
    View to display all responses by the current user for a specific assessment.
    """
    assessment = get_object_or_404(Assessment, pk=pk)
    responses = UserResponse.objects.filter(user=request.user, assessment=assessment)
    return render(request, 'assessments/assessment_results.html', {'assessment': assessment, 'responses': responses})

class AssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assessments to be viewed or edited.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    
    def get_queryset(self):
        """
        Optionally filter by active assessments.
        """
        queryset = Assessment.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

class UserResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user responses to be viewed or edited.
    """
    queryset = UserResponse.objects.all()
    serializer_class = UserResponseSerializer
