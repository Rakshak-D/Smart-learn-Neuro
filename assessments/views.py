from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import Assessment, Response
from .serializers import AssessmentSerializer, ResponseSerializer

@login_required
def assessment_list(request):
    """
    View to display all assessments.
    """
    assessments = Assessment.objects.all()
    return render(request, 'assessments/assessment_list.html', {'assessments': assessments})

@login_required
def assessment_detail(request, pk):
    """
    View to display a single assessment and handle response submission.
    """
    assessment = get_object_or_404(Assessment, pk=pk)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text')
        # Create a new Response object linked to the current user and assessment
        Response.objects.create(user=request.user, assessment=assessment, response_text=response_text)
        return redirect('assessment_results', pk=assessment.pk)
    
    return render(request, 'assessments/assessment_detail.html', {'assessment': assessment})

@login_required
def assessment_results(request, pk):
    """
    View to display all responses by the current user for a specific assessment.
    """
    assessment = get_object_or_404(Assessment, pk=pk)
    responses = Response.objects.filter(user=request.user, assessment=assessment)
    return render(request, 'assessments/assessment_results.html', {'assessment': assessment, 'responses': responses})

class AssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on assessments.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

class ResponseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on responses.
    """
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
