from django.shortcuts import render, get_object_or_404
from .models import Project, Technology

def project_list_view(request):
    category = request.GET.get('category', '').strip()
    projects_qs = Project.objects.prefetch_related('technologies').order_by('order', 'id')
    
    if category:
        projects_qs = projects_qs.filter(category__icontains=category)
        
    categories = (
        Project.objects.values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    context = {
        'projects': projects_qs,
        'categories': categories,
        'selected_category': category,
        'total_count': Project.objects.count(),
    }
    return render(request, 'projects.html', context)


def project_detail_view(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related('technologies', 'images'),
        slug=slug
    )
    
    # Navigation to next/previous projects
    all_projects = list(Project.objects.order_by('order', 'id'))
    current_idx = -1
    for idx, p in enumerate(all_projects):
        if p.id == project.id:
            current_idx = idx
            break
            
    prev_project = all_projects[current_idx - 1] if current_idx > 0 else all_projects[-1]
    next_project = all_projects[current_idx + 1] if current_idx < len(all_projects) - 1 else all_projects[0]

    context = {
        'project': project,
        'features': project.get_features_list(),
        'flow_stages': project.get_flow_stages(),
        'prev_project': prev_project,
        'next_project': next_project,
    }
    return render(request, 'project_detail.html', context)
