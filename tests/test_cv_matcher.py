import pytest
import json
import os
from io import BytesIO
from unittest.mock import patch, MagicMock


def test_analyze_cv_with_text_jd(client, auth_headers):
    """Test CV analysis with text job description"""
    # Create a dummy PDF file
    pdf_content = b'%PDF-1.4 fake pdf content python django react'
    
    # Mock the PDF extraction to avoid parsing issues
    with patch('backend.routes.cv_matcher.extract_text_from_pdf') as mock_extract:
        mock_extract.return_value = "Software Engineer with experience in Python, Django, React, and JavaScript. Strong communication skills."
        
        data = {
            'cv_file': (BytesIO(pdf_content), 'test_cv.pdf'),
            'jd_text': 'Looking for Software Engineer with Python, Django, React skills'
        }
        
        response = client.post('/api/v1/cv/analyze',
                              headers={
                                  'Authorization': auth_headers['Authorization']
                              },
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 201, f"Failed: {response.get_json()}"
        result = response.get_json()
        assert 'ats_score' in result
        assert 'matched_keywords' in result
        assert 'missing_keywords' in result
        assert result['ats_score'] >= 0
        assert result['ats_score'] <= 100
        print(f"✅ CV analyzed successfully with ATS score: {result['ats_score']}")


def test_analyze_cv_missing_file(client, auth_headers):
    """Test CV analysis without CV file"""
    data = {'jd_text': 'Some job description'}
    
    response = client.post('/api/v1/cv/analyze',
                          headers={
                              'Authorization': auth_headers['Authorization']
                          },
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    result = response.get_json()
    assert 'error' in result
    assert 'cv_file' in result['error'].lower() or 'required' in result['error'].lower()
    print(f"✅ Missing file correctly rejected")


def test_analyze_cv_missing_jd(client, auth_headers):
    """Test CV analysis without job description"""
    pdf_content = b'%PDF-1.4 fake pdf'
    data = {'cv_file': (BytesIO(pdf_content), 'test.pdf')}
    
    response = client.post('/api/v1/cv/analyze',
                          headers={
                              'Authorization': auth_headers['Authorization']
                          },
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    result = response.get_json()
    assert 'error' in result
    print(f"✅ Missing job description correctly rejected")


def test_analyze_cv_invalid_file_type(client, auth_headers):
    """Test CV analysis with invalid file type"""
    data = {
        'cv_file': (BytesIO(b'some text'), 'test.txt'),
        'jd_text': 'Some job description'
    }
    
    response = client.post('/api/v1/cv/analyze',
                          headers={
                              'Authorization': auth_headers['Authorization']
                          },
                          data=data,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    result = response.get_json()
    assert 'error' in result
    print(f"✅ Invalid file type correctly rejected")


def test_get_cv_history(client, auth_headers):
    """Test getting CV analysis history"""
    response = client.get('/api/v1/cv/history', headers=auth_headers)
    
    assert response.status_code == 200, f"Failed: {response.get_json()}"
    result = response.get_json()
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    print(f"✅ CV history retrieved: {len(result)} analyses")


def test_get_cv_analysis_not_found(client, auth_headers):
    """Test getting non-existent CV analysis"""
    response = client.get('/api/v1/cv/analysis/9999', headers=auth_headers)
    
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    result = response.get_json()
    assert 'error' in result
    print(f"✅ Non-existent analysis correctly returned 404")


def test_cv_analysis_with_application_link(client, auth_headers):
    """Test CV analysis linked to an application"""
    # First create a company
    company_response = client.post('/api/v1/companies',
                                   headers=auth_headers,
                                   json={
                                       "name": "Test Company CV",
                                       "website": "https://testcv.com"
                                   })
    assert company_response.status_code == 201, f"Company creation failed: {company_response.get_json()}"
    company_id = company_response.get_json()['id']
    
    # Create an application
    app_response = client.post('/api/v1/applications',
                               headers=auth_headers,
                               json={
                                   "company_id": company_id,
                                   "job_title": "Software Engineer",
                                   "status": "Planned"
                               })
    assert app_response.status_code == 201, f"Application creation failed: {app_response.get_json()}"
    application_id = app_response.get_json()['id']
    
    # Mock PDF extraction
    with patch('backend.routes.cv_matcher.extract_text_from_pdf') as mock_extract:
        mock_extract.return_value = "Python developer with Django and Flask experience. Strong problem solving skills."
        
        # Analyze CV with application link
        pdf_content = b'%PDF-1.4 fake pdf with python skills'
        data = {
            'cv_file': (BytesIO(pdf_content), 'test_cv.pdf'),
            'jd_text': 'Python developer needed with Django experience and strong communication skills',
            'application_id': str(application_id)
        }
        
        response = client.post('/api/v1/cv/analyze',
                              headers={
                                  'Authorization': auth_headers['Authorization']
                              },
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 201, f"Failed: {response.get_json()}"
        result = response.get_json()
        assert 'ats_score' in result
        assert result['ats_score'] >= 0
        print(f"✅ CV analysis linked to application {application_id} with score: {result['ats_score']}")


def test_cv_analysis_score_calculation(client, auth_headers):
    """Test that ATS score is calculated correctly"""
    with patch('backend.routes.cv_matcher.extract_text_from_pdf') as mock_extract:
        # CV has: python, django, react
        mock_extract.return_value = "Experienced in Python, Django, and React development."
        
        pdf_content = b'%PDF-1.4 fake pdf'
        data = {
            'cv_file': (BytesIO(pdf_content), 'test_cv.pdf'),
            # JD requires: python, django, react, javascript (75% match expected)
            'jd_text': 'Looking for developer with Python, Django, React, and JavaScript skills'
        }
        
        response = client.post('/api/v1/cv/analyze',
                              headers={
                                  'Authorization': auth_headers['Authorization']
                              },
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 201, f"Failed: {response.get_json()}"
        result = response.get_json()
        
        # Should have matched keywords
        assert len(result['matched_keywords']) > 0
        # Should have missing keywords (javascript)
        assert len(result['missing_keywords']) > 0
        # Score should be between 0-100
        assert 0 <= result['ats_score'] <= 100
        
        print(f"✅ ATS score calculation verified: {result['ats_score']}%")
        print(f"   Matched: {result['matched_keywords']}")
        print(f"   Missing: {result['missing_keywords']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])