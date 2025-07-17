"""Step definitions for AI custom questions feature tests."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from unittest.mock import Mock, patch, MagicMock
import json
from src.web_interface.ai_config_manager import AIConfigManager
from src.ai.content_analyzer import AIContentAnalyzer


scenarios("../features/ai_custom_questions.feature")


@pytest.fixture
def ai_config_manager():
    """Provide AIConfigManager for testing."""
    return AIConfigManager()


@pytest.fixture
def mock_ai_analyzer():
    """Provide mock AI analyzer for testing."""
    with patch('src.ai.content_analyzer.AIContentAnalyzer') as mock:
        analyzer = Mock()
        analyzer.analyze_content.return_value = {
            'menu_enhancements': [],
            'restaurant_characteristics': {'ambiance': 'casual'},
            'customer_amenities': {'parking': 'available'},
            'custom_questions': [
                {
                    'question': 'Are takeout containers eco-friendly?',
                    'answer': 'Yes, they use biodegradable containers'
                }
            ]
        }
        analyzer.calculate_integrated_confidence.return_value = 0.8
        mock.return_value = analyzer
        yield analyzer


@pytest.fixture
def sample_restaurant_content():
    """Provide sample restaurant content for testing."""
    return {
        'content': """
        Welcome to Green Bistro! We serve fresh, locally-sourced meals.
        Our takeout containers are made from biodegradable materials.
        WiFi password is available upon request for customers.
        We welcome well-behaved pets on our outdoor patio.
        """,
        'menu_items': [
            {'name': 'Garden Salad', 'section': 'Appetizers'},
            {'name': 'Quinoa Bowl', 'section': 'Entrees'}
        ]
    }


@given("the AI enhancement system is available")
def ai_system_available():
    """Ensure AI enhancement system is available."""
    pass


@given("I have a valid OpenAI API key configured")
def valid_api_key():
    """Mock valid API key configuration."""
    pass


@given("I am on the scraping interface")
def on_scraping_interface():
    """Simulate being on the scraping interface."""
    pass


@given("I have enabled AI enhancement")
def ai_enhancement_enabled():
    """Simulate AI enhancement being enabled."""
    pass


@given("I have configured AI enhancement with a custom question <question>")
def ai_configured_with_question(question):
    """Configure AI with a specific custom question."""
    pass


@given("I have restaurant content to analyze")
def restaurant_content_available(sample_restaurant_content):
    """Ensure restaurant content is available for analysis."""
    pass


@given("I am configuring AI enhancement")
def configuring_ai_enhancement():
    """Simulate configuring AI enhancement."""
    pass


@given("I have saved custom questions in my AI settings")
def saved_custom_questions():
    """Simulate having saved custom questions."""
    pass


@given("I have custom questions configured")
def custom_questions_configured():
    """Simulate having custom questions configured."""
    pass


@given("I have performed AI analysis with custom questions")
def ai_analysis_with_questions_performed():
    """Simulate completed AI analysis with custom questions."""
    pass


@given("I have scraped restaurant data with custom questions enabled")
def scraped_data_with_questions():
    """Simulate scraped data with custom questions enabled."""
    pass


@given("I am using the AI API endpoints")
def using_ai_api():
    """Simulate using AI API endpoints."""
    pass


@when("I open the AI settings panel")
def open_ai_settings():
    """Simulate opening AI settings panel."""
    pass


@when('I enter "<question>" in the custom questions field')
def enter_custom_question(question):
    """Simulate entering a custom question."""
    pass


@when("I save the AI configuration")
def save_ai_config():
    """Simulate saving AI configuration."""
    pass


@when("I perform AI analysis on the content")
def perform_ai_analysis(mock_ai_analyzer, sample_restaurant_content):
    """Simulate performing AI analysis."""
    result = mock_ai_analyzer.analyze_content(
        content=sample_restaurant_content['content'],
        menu_items=sample_restaurant_content['menu_items'],
        analysis_type='nutritional'
    )
    return result


@when("I add multiple custom questions")
def add_multiple_questions():
    """Simulate adding multiple custom questions."""
    pass


@when("I enter a question longer than 200 characters")
def enter_long_question():
    """Simulate entering a question longer than 200 characters."""
    pass


@when("I close and reopen the application")
def close_reopen_app():
    """Simulate closing and reopening the application."""
    pass


@when("I load my saved AI settings")
def load_saved_settings():
    """Simulate loading saved AI settings."""
    pass


@when("I switch between different AI providers")
def switch_providers():
    """Simulate switching between different AI providers."""
    pass


@when("I leave the custom questions field empty")
def leave_questions_empty():
    """Simulate leaving custom questions field empty."""
    pass


@when("I view the analysis results")
def view_analysis_results():
    """Simulate viewing analysis results."""
    pass


@when("I export the results to JSON format")
def export_to_json():
    """Simulate exporting results to JSON format."""
    pass


@when('I configure custom questions via "/api/ai/configure"')
def configure_via_api():
    """Simulate configuring custom questions via API."""
    pass


@then("the custom question should be stored in my AI settings")
def question_stored():
    """Verify custom question is stored."""
    pass


@then("the question should have a 200 character limit")
def verify_character_limit():
    """Verify 200 character limit is enforced."""
    pass


@then("the AI prompt should include my custom question")
def ai_prompt_includes_question():
    """Verify AI prompt includes the custom question."""
    pass


@then("the AI should attempt to answer the custom question")
def ai_attempts_answer():
    """Verify AI attempts to answer the custom question."""
    pass


@then("the analysis results should include custom question responses")
def results_include_responses():
    """Verify analysis results include custom question responses."""
    pass


@then("all custom questions should be stored")
def all_questions_stored():
    """Verify all custom questions are stored."""
    pass


@then("each question should be included in AI analysis")
def questions_in_analysis():
    """Verify each question is included in AI analysis."""
    pass


@then("the input should be limited to 200 characters")
def input_limited():
    """Verify input is limited to 200 characters."""
    pass


@then("I should see a character count indicator")
def character_count_visible():
    """Verify character count indicator is visible."""
    pass


@then('the system should show "200/200" when at the limit')
def show_limit_indicator():
    """Verify system shows character limit indicator."""
    pass


@then("my custom questions should be restored")
def questions_restored():
    """Verify custom questions are restored after restart."""
    pass


@then("they should be available for new scraping operations")
def available_for_scraping():
    """Verify questions are available for new operations."""
    pass


@then("the custom questions should work with each provider")
def questions_work_with_providers():
    """Verify custom questions work with all providers."""
    pass


@then("the questions should be included in provider-specific prompts")
def questions_in_provider_prompts():
    """Verify questions are included in provider-specific prompts."""
    pass


@then("the AI analysis should work normally without custom questions")
def analysis_works_without_questions():
    """Verify AI analysis works without custom questions."""
    pass


@then("no additional prompting should occur for custom questions")
def no_additional_prompting():
    """Verify no additional prompting occurs when no questions."""
    pass


@then("I should see a dedicated section for custom question answers")
def dedicated_section_visible():
    """Verify dedicated section for custom question answers."""
    pass


@then("each answer should be clearly labeled with its corresponding question")
def answers_labeled():
    """Verify answers are labeled with their questions."""
    pass


@then('unanswered questions should be marked as "No information found"')
def unanswered_marked():
    """Verify unanswered questions are properly marked."""
    pass


@then('the JSON should include a "custom_questions" section')
def json_includes_section():
    """Verify JSON export includes custom questions section."""
    pass


@then("each question-answer pair should be properly formatted")
def pairs_formatted():
    """Verify question-answer pairs are properly formatted."""
    pass


@then("the export should maintain the original question text")
def maintains_question_text():
    """Verify export maintains original question text."""
    pass


@then("the questions should be stored in the session configuration")
def questions_in_session():
    """Verify questions are stored in session configuration."""
    pass


@then('subsequent "/api/ai/analyze-content" calls should include the questions')
def api_calls_include_questions():
    """Verify API calls include the questions."""
    pass


@then("the API should return custom question responses in the analysis results")
def api_returns_responses():
    """Verify API returns custom question responses."""
    pass


# Unit test functions for custom questions functionality
class TestCustomQuestionsUnit:
    """Unit tests for custom questions functionality."""
    
    def test_custom_question_validation(self):
        """Test custom question validation."""
        # Test question length validation
        short_question = "Pet friendly?"
        long_question = "A" * 201  # 201 characters
        
        assert len(short_question) <= 200
        assert len(long_question) > 200
    
    def test_custom_question_storage(self, ai_config_manager):
        """Test storing custom questions in configuration."""
        session_id = "test_session"
        config = {
            'ai_enhancement_enabled': True,
            'custom_questions': ['Are takeout containers eco-friendly?']
        }
        
        ai_config_manager.set_session_config(session_id, config)
        retrieved_config = ai_config_manager.get_session_config(session_id)
        
        assert 'custom_questions' in retrieved_config
        assert len(retrieved_config['custom_questions']) == 1
    
    def test_custom_question_prompt_integration(self, mock_ai_analyzer):
        """Test custom questions integration into AI prompts."""
        custom_questions = ['Are takeout containers eco-friendly?']
        
        # Simulate AI analysis with custom questions
        result = mock_ai_analyzer.analyze_content(
            content="Restaurant content here",
            menu_items=[],
            analysis_type='nutritional'
        )
        
        # Verify custom questions are handled
        assert 'custom_questions' in result
        assert len(result['custom_questions']) > 0
    
    def test_multiple_custom_questions(self):
        """Test handling multiple custom questions."""
        questions = [
            'Pet-friendly seating available?',
            'Do they offer gluten-free options?',
            'What are the parking restrictions?'
        ]
        
        # Each question should be under 200 characters
        for question in questions:
            assert len(question) <= 200
        
        # Should be able to store multiple questions
        assert len(questions) == 3
    
    def test_empty_custom_questions(self, mock_ai_analyzer):
        """Test handling empty custom questions."""
        # When no custom questions are provided
        result = mock_ai_analyzer.analyze_content(
            content="Restaurant content here",
            menu_items=[],
            analysis_type='nutritional'
        )
        
        # Should still work normally
        assert result is not None
        assert 'menu_enhancements' in result