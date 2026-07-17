import pytest
from pydantic import BaseModel
from app.llm.router import LLMRouter
from app.llm.exceptions import AllProvidersFailedError


class DummySchema(BaseModel):
    name: str


def test_llm_router_first_success(mocker):
    """Test that the router returns the first successful provider's response and skips the rest."""
    router = LLMRouter()

    mock_models = []
    for provider in router.providers:
        mock_model = mocker.MagicMock()
        mocker.patch.object(
            provider, "get_structured_model", return_value=mock_model
        )
        mock_models.append(mock_model)

    mock_models[0].invoke.return_value = DummySchema(name="First Success")

    res = router.invoke_structured("hello", DummySchema)
    assert res.name == "First Success"

    mock_models[0].invoke.assert_called_once()
    for mm in mock_models[1:]:
        mm.invoke.assert_not_called()


def test_llm_router_failover_to_next(mocker):
    """Test that the router fails over to the next provider when one fails, and sets cooldown."""
    router = LLMRouter()

    mock_models = []
    for provider in router.providers:
        mock_model = mocker.MagicMock()
        mocker.patch.object(
            provider, "get_structured_model", return_value=mock_model
        )
        mock_models.append(mock_model)

    # First fails, second succeeds
    mock_models[0].invoke.side_effect = Exception("First Provider Error")
    mock_models[1].invoke.return_value = DummySchema(name="Second Success")

    res = router.invoke_structured("hello", DummySchema)
    assert res.name == "Second Success"

    # Verify first provider was called and is now in cooldown
    mock_models[0].invoke.assert_called_once()
    assert router.states[router.providers[0].name].is_in_cooldown

    # Verify second provider was called
    mock_models[1].invoke.assert_called_once()

    # Verify remaining providers were not called
    for mm in mock_models[2:]:
        mm.invoke.assert_not_called()


def test_llm_router_skips_cooldown_provider(mocker):
    """Test that providers in cooldown are bypassed entirely in subsequent calls."""
    router = LLMRouter()

    mock_models = []
    for provider in router.providers:
        mock_model = mocker.MagicMock()
        mocker.patch.object(
            provider, "get_structured_model", return_value=mock_model
        )
        mock_models.append(mock_model)

    # Make first fail, second succeed on first call
    mock_models[0].invoke.side_effect = Exception("Failed")
    mock_models[1].invoke.return_value = DummySchema(name="Fallback")

    # Run first time
    router.invoke_structured("hello", DummySchema)

    # Reset mock call counters
    mock_models[0].invoke.reset_mock()
    mock_models[1].invoke.reset_mock()

    # Run second time: first provider should be skipped automatically
    router.invoke_structured("hello", DummySchema)

    mock_models[0].invoke.assert_not_called()
    mock_models[1].invoke.assert_called_once()


def test_llm_router_all_providers_fail(mocker):
    """Test that AllProvidersFailedError is raised if all providers raise exceptions."""
    router = LLMRouter()

    for provider in router.providers:
        mock_model = mocker.MagicMock()
        mock_model.invoke.side_effect = Exception("Fatal Provider Error")
        mocker.patch.object(
            provider, "get_structured_model", return_value=mock_model
        )

    with pytest.raises(AllProvidersFailedError):
        router.invoke_structured("hello", DummySchema)
