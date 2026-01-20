"""
Debug settings for performance profiling.

To enable profiling, add this to your settings.py:
    from debug_settings import add_profiling_settings
    add_profiling_settings(locals())

Or copy the relevant settings manually.
"""

def add_profiling_settings(settings_dict):
    """
    Add Silk profiler settings to Django settings.
    
    Usage in settings.py:
        from debug_settings import add_profiling_settings
        add_profiling_settings(locals())
    """
    
    # Add silk to installed apps
    if 'silk' not in settings_dict.get('INSTALLED_APPS', []):
        settings_dict['INSTALLED_APPS'] = list(settings_dict.get('INSTALLED_APPS', [])) + ['silk']
    
    # Add silk middleware - must be after authentication middleware
    middleware = list(settings_dict.get('MIDDLEWARE', []))
    if 'silk.middleware.SilkyMiddleware' not in middleware:
        # Insert after authentication middleware
        auth_index = next(
            (i for i, m in enumerate(middleware) if 'auth' in m.lower()), 
            len(middleware)
        )
        middleware.insert(auth_index + 1, 'silk.middleware.SilkyMiddleware')
        settings_dict['MIDDLEWARE'] = middleware
    
    # Silk configuration
    settings_dict['SILKY_PYTHON_PROFILER'] = True
    settings_dict['SILKY_PYTHON_PROFILER_BINARY'] = True
    settings_dict['SILKY_META'] = True
    settings_dict['SILKY_MAX_RECORDED_REQUESTS'] = 1000
    settings_dict['SILKY_MAX_REQUEST_BODY_SIZE'] = -1  # Unlimited
    settings_dict['SILKY_MAX_RESPONSE_BODY_SIZE'] = -1  # Unlimited
    
    # Optional: Limit which requests are profiled
    # settings_dict['SILKY_INTERCEPT_PERCENT'] = 50  # Profile 50% of requests
    
    print("✅ Silk profiling enabled. Access at: http://localhost:8000/silk/")


# Configuration to add to urls.py:
SILK_URLPATTERNS = """
# Add to backend/urls.py:
from django.urls import path, include

urlpatterns = [
    # ... existing patterns ...
    path('silk/', include('silk.urls', namespace='silk')),
]
"""
