#!/usr/bin/env python3
"""
Quick test script to verify all import statements work correctly
after renaming from __init__.py to descriptive module names.
"""

def test_imports():
    """Test all major module imports"""
    print("Testing imports after renaming from __init__.py to descriptive names...")
    
    try:
        # Test core config
        from app.core.config import settings
        print("✅ app.core.config imported successfully")
        
        # Test database models  
        from app.models.database_models import UserSession, ConversationTree
        print("✅ app.models.database_models imported successfully")
        
        # Test services
        from app.services.research_services import ConversationService
        print("✅ app.services.research_services imported successfully")
        
        # Test schemas
        from app.schemas.api_schemas import ErrorResponse, ConversationResponse
        print("✅ app.schemas.api_schemas imported successfully")
        
        # Test database config
        from app.db.database_config import get_db
        print("✅ app.db.database_config imported successfully")
        
        # Test API routes 
        from app.api.api_routes import router
        print("✅ app.api.api_routes imported successfully")
        
        # Test v1 routes
        from app.api.v1.v1_routes import router as v1_router
        print("✅ app.api.v1.v1_routes imported successfully")
        
        print("\n🎉 All imports successful! Descriptive module names are working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
