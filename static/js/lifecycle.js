/**
 * "BEHIND THE REQUEST" — Interactive API Lifecycle Component
 * Visualizing the journey of a request from client to database and back to JSON
 */

document.addEventListener('DOMContentLoaded', () => {
  initRequestLifecycle();
});

function initRequestLifecycle() {
  const nodes = document.querySelectorAll('.pipeline-node');
  const headingEl = document.getElementById('lifecycle-node-title');
  const descEl = document.getElementById('lifecycle-node-desc');
  const metricLatency = document.getElementById('lifecycle-metric-latency');
  const metricPurpose = document.getElementById('lifecycle-metric-purpose');
  const codeEl = document.getElementById('lifecycle-code');
  const simBtn = document.getElementById('lifecycle-run-sim');

  if (!nodes.length || !headingEl || !descEl || !codeEl) return;

  const stepsData = {
    1: {
      title: "01. HTTP Client Request",
      desc: "The browser or client sends an asynchronous HTTP GET request with headers (Accept: application/json, Bearer Auth Token, User-Agent) through the network.",
      latency: "0.2ms (Ingress)",
      purpose: "Network Ingress & TLS Handshake",
      code: `GET /api/v1/projects/ HTTP/1.1
Host: ujval.dev
Accept: application/json
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64)`
    },
    2: {
      title: "02. Django URL Dispatcher",
      desc: "The request hits urls.py. Django's URL resolver matches the path regex/slug pattern and routes the execution context to the designated view controller.",
      latency: "0.4ms",
      purpose: "Regex Routing & Middleware Stack",
      code: `# config/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/v1/projects/', include('projects.api_urls')),
]

# projects/api_urls.py
urlpatterns = [
    path('', views.ProjectListAPIView.as_view(), name='project-list'),
]`
    },
    3: {
      title: "03. DRF View & Permissions",
      desc: "Django REST Framework View intercepts the request, runs authentication checks (JWT/Session), evaluates permission classes, and triggers the action handler.",
      latency: "0.8ms",
      purpose: "Auth, Throttling & Business Logic",
      code: `class ProjectListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(featured=True)\\
                              .prefetch_related('technologies')`
    },
    4: {
      title: "04. DRF Serializer Schema",
      desc: "Serializers define the strict JSON schema, perform field transformations, validate input parameters, and convert Python model instances to native datatypes.",
      latency: "1.2ms",
      purpose: "Data Serialization & Type Safety",
      code: `class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True, read_only=True)
    live_status = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['project_number', 'title', 'slug', 'category', 'technologies']`
    },
    5: {
      title: "05. QuerySet & ORM Optimization",
      desc: "Django's ORM lazily constructs an optimized SQL query. Using select_related() and prefetch_related() prevents the N+1 query problem across relational tables.",
      latency: "1.5ms",
      purpose: "Query Compilation & Cache Check",
      code: `# QuerySet is evaluated only when data is accessed:
queryset = Project.objects.filter(featured=True)\\
                          .select_related('profile')\\
                          .prefetch_related('technologies', 'images')\\
                          .order_by('order')`
    },
    6: {
      title: "06. Database Engine (PostgreSQL / SQLite)",
      desc: "The database executes the compiled SQL query utilizing B-Tree indexes on order and category columns. Relational constraints and ACID transactions are upheld.",
      latency: "2.1ms",
      purpose: "Index Scan & Disk / Buffer Cache Read",
      code: `SELECT "projects_project"."id", "projects_project"."title", 
       "projects_project"."order"
FROM "projects_project"
WHERE "projects_project"."featured" = true
ORDER BY "projects_project"."order" ASC;
-- Index Scan: projects_project_order_idx`
    },
    7: {
      title: "07. HTTP 200 OK JSON Response",
      desc: "Django packs the serialized payload into an HttpResponse with Content-Type: application/json, sets security headers (X-Content-Type-Options, CSRF), and streams back.",
      latency: "0.5ms (Egress)",
      purpose: "Response Formatting & Compression",
      code: `HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Encoding: gzip
Cache-Control: max-age=300, public
X-Response-Time: 6.7ms

{"count": 6, "status": 200, "results": [...]}`
    }
  };

  function selectStep(stepNum) {
    const data = stepsData[stepNum];
    if (!data) return;

    nodes.forEach(n => {
      if (parseInt(n.dataset.step, 10) === stepNum) {
        n.classList.add('is-active');
      } else {
        n.classList.remove('is-active');
      }
    });

    headingEl.textContent = data.title;
    descEl.textContent = data.desc;
    if (metricLatency) metricLatency.textContent = data.latency;
    if (metricPurpose) metricPurpose.textContent = data.purpose;
    codeEl.textContent = data.code;
  }

  // Node click events
  nodes.forEach(node => {
    node.addEventListener('click', () => {
      const step = parseInt(node.dataset.step, 10);
      selectStep(step);
    });
  });

  // Automated Simulation Run
  if (simBtn) {
    let isSimulating = false;
    simBtn.addEventListener('click', () => {
      if (isSimulating) return;
      isSimulating = true;
      simBtn.textContent = 'RUNNING SIMULATION...';
      simBtn.classList.add('active');

      let current = 1;
      selectStep(current);

      const simInterval = setInterval(() => {
        current++;
        if (current <= 7) {
          selectStep(current);
        } else {
          clearInterval(simInterval);
          isSimulating = false;
          simBtn.textContent = 'SIMULATION COMPLETE (200 OK)';
          setTimeout(() => {
            simBtn.textContent = 'RE-RUN SIMULATION';
            simBtn.classList.remove('active');
          }, 2000);
        }
      }, 700);
    });
  }

  // Default initialize with step 1
  selectStep(1);
}
