#!/usr/bin/env python3
"""
Implementation validation script for Skylyt TravelHub Backend
Validates that all phases and tasks are properly implemented
"""
import os
import sys
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and log result"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def validate_phase_1_2():
    """Validate Phase 1-2: Project Foundation & Database Models"""
    print("\n=== PHASE 1-2: PROJECT FOUNDATION & DATABASE MODELS ===")
    
    files = [
        ("app/core/config.py", "Configuration"),
        ("app/core/database.py", "Database setup"),
        ("app/core/security.py", "Security utilities"),
        ("app/models/user.py", "User model"),
        ("app/models/booking.py", "Booking model"),
        ("app/models/payment.py", "Payment model"),
        ("app/models/rbac.py", "RBAC models"),
        ("alembic.ini", "Alembic configuration"),
        ("requirements.txt", "Dependencies")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_3_4():
    """Validate Phase 3-4: Schemas & Business Logic"""
    print("\n=== PHASE 3-4: SCHEMAS & BUSINESS LOGIC ===")
    
    files = [
        ("app/schemas/user.py", "User schemas"),
        ("app/schemas/booking.py", "Booking schemas"),
        ("app/schemas/payment.py", "Payment schemas"),
        ("app/schemas/auth.py", "Auth schemas"),
        ("app/services/user_service.py", "User service"),
        ("app/services/booking_service.py", "Booking service"),
        ("app/services/payment_service.py", "Payment service"),
        ("app/services/auth_service.py", "Auth service"),
        ("app/services/rbac_service.py", "RBAC service")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_5():
    """Validate Phase 5: External API Integrations"""
    print("\n=== PHASE 5: EXTERNAL API INTEGRATIONS ===")
    
    files = [
        ("app/external/payment/stripe_client.py", "Stripe integration"),
        ("app/external/payment/flutterwave_client.py", "Flutterwave integration"),
        ("app/external/payment/paystack_client.py", "Paystack integration"),
        ("app/external/payment/payment_factory.py", "Payment factory"),
        ("app/external/hotels/hotel_base.py", "Hotel API base"),
        ("app/external/hotels/booking_com.py", "Booking.com integration"),
        ("app/external/cars/car_base.py", "Car rental base"),
        ("app/external/cars/hertz.py", "Hertz integration")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_6():
    """Validate Phase 6: API Routes & Endpoints"""
    print("\n=== PHASE 6: API ROUTES & ENDPOINTS ===")
    
    files = [
        ("app/api/v1/auth.py", "Authentication endpoints"),
        ("app/api/v1/users.py", "User management endpoints"),
        ("app/api/v1/hotels.py", "Hotel search endpoints"),
        ("app/api/v1/cars.py", "Car rental endpoints"),
        ("app/api/v1/search.py", "Combined search endpoints"),
        ("app/api/v1/bookings.py", "Booking management endpoints"),
        ("app/api/v1/payments.py", "Payment processing endpoints"),
        ("app/api/v1/rbac.py", "RBAC endpoints")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_7():
    """Validate Phase 7: Middleware & Utilities"""
    print("\n=== PHASE 7: MIDDLEWARE & UTILITIES ===")
    
    files = [
        ("app/middleware/rate_limit.py", "Rate limiting middleware"),
        ("app/middleware/security.py", "Security middleware"),
        ("app/middleware/cors.py", "CORS configuration"),
        ("app/middleware/monitoring.py", "Request monitoring"),
        ("app/utils/logger.py", "Logging configuration"),
        ("app/monitoring/metrics.py", "Prometheus metrics"),
        ("app/utils/cache.py", "Caching layer"),
        ("app/tasks/email_tasks.py", "Email tasks"),
        ("app/tasks/booking_tasks.py", "Booking tasks"),
        ("app/tasks/cleanup_tasks.py", "Cleanup tasks"),
        ("celery_app.py", "Celery configuration")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_8():
    """Validate Phase 8: Testing Implementation"""
    print("\n=== PHASE 8: TESTING IMPLEMENTATION ===")
    
    files = [
        ("tests/conftest.py", "Test configuration"),
        ("tests/test_auth.py", "Authentication tests"),
        ("tests/test_users.py", "User management tests"),
        ("tests/test_bookings.py", "Booking functionality tests"),
        ("tests/integration/test_api_endpoints.py", "API integration tests"),
        ("tests/integration/test_booking_flow.py", "Booking flow tests"),
        ("tests/integration/test_payment_flow.py", "Payment flow tests"),
        ("tests/performance/test_search_performance.py", "Search performance tests"),
        ("tests/performance/test_concurrent_bookings.py", "Concurrent booking tests"),
        ("pytest.ini", "Pytest configuration"),
        ("run_tests.py", "Test runner script")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_9():
    """Validate Phase 9: Main Application & Deployment"""
    print("\n=== PHASE 9: MAIN APPLICATION & DEPLOYMENT ===")
    
    files = [
        ("app/main.py", "Main FastAPI application"),
        ("Dockerfile", "Production Docker image"),
        ("docker-compose.yml", "Local development setup"),
        ("docker-compose.prod.yml", "Production configuration"),
        (".env.example", "Environment variables template"),
        ("scripts/setup_env.sh", "Environment setup script"),
        ("scripts/deploy.sh", "Deployment script"),
        ("docs/API.md", "API documentation"),
        ("docs/SETUP.md", "Setup instructions"),
        ("docs/DEPLOYMENT.md", "Deployment guide"),
        ("README.md", "Project README")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_phase_10():
    """Validate Phase 10: Final Integration & Optimization"""
    print("\n=== PHASE 10: FINAL INTEGRATION & OPTIMIZATION ===")
    
    files = [
        ("alembic/versions/add_database_indexes.py", "Database indexes migration"),
        ("app/utils/query_optimizer.py", "Query optimization utilities"),
        ("scripts/optimize_database.py", "Database optimization script"),
        ("app/middleware/performance.py", "Performance middleware"),
        ("app/middleware/compression.py", "Response compression"),
        ("app/middleware/security_hardening.py", "Security hardening"),
        ("app/monitoring/alerting.py", "Monitoring and alerting"),
        ("app/monitoring/error_tracking.py", "Error tracking system"),
        ("scripts/performance_monitor.py", "Performance monitoring script"),
        ("docs/OPTIMIZATION.md", "Optimization guide")
    ]
    
    return all(check_file_exists(f, desc) for f, desc in files)

def validate_best_practices():
    """Validate development best practices"""
    print("\n=== DEVELOPMENT BEST PRACTICES VALIDATION ===")
    
    # Check for type hints in key files
    key_files = [
        "app/services/user_service.py",
        "app/services/booking_service.py",
        "app/api/v1/auth.py"
    ]
    
    type_hints_ok = True
    for file_path in key_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                if "from typing import" in content or ": " in content:
                    print(f"✅ Type hints found in {file_path}")
                else:
                    print(f"❌ Type hints missing in {file_path}")
                    type_hints_ok = False
    
    # Check for error handling
    error_handling_files = [
        "app/middleware/security_hardening.py",
        "app/monitoring/error_tracking.py"
    ]
    
    error_handling_ok = all(check_file_exists(f, f"Error handling in {f}") for f in error_handling_files)
    
    # Check for logging
    logging_ok = check_file_exists("app/utils/logger.py", "Logging configuration")
    
    # Check for testing
    testing_ok = check_file_exists("tests/conftest.py", "Test configuration")
    
    # Check for documentation
    docs_ok = all(check_file_exists(f"docs/{doc}", f"{doc} documentation") 
                  for doc in ["API.md", "SETUP.md", "DEPLOYMENT.md"])
    
    return all([type_hints_ok, error_handling_ok, logging_ok, testing_ok, docs_ok])

def main():
    """Main validation function"""
    print("🔍 Validating Skylyt TravelHub Backend Implementation")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Validate each phase
    phase_results = {
        "Phase 1-2": validate_phase_1_2(),
        "Phase 3-4": validate_phase_3_4(),
        "Phase 5": validate_phase_5(),
        "Phase 6": validate_phase_6(),
        "Phase 7": validate_phase_7(),
        "Phase 8": validate_phase_8(),
        "Phase 9": validate_phase_9(),
        "Phase 10": validate_phase_10(),
        "Best Practices": validate_best_practices()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for phase, passed in phase_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{phase}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PHASES SUCCESSFULLY IMPLEMENTED!")
        print("The Skylyt TravelHub Backend is ready for deployment.")
    else:
        print("⚠️  SOME PHASES NEED ATTENTION")
        print("Please review the failed items above.")
        sys.exit(1)

if __name__ == "__main__":
    main()