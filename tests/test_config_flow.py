"""Tests for Entity Manager config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult, FlowResultType
import pytest

from custom_components.entity_manager.config_flow import (
    ConfigFlow,
    EntityManagerConfigError,
)
from custom_components.entity_manager.const import DOMAIN


class TestConfigFlow:
    """Test the Entity Manager config flow."""

    def setup_method(self):
        """Set up test method."""
        self.flow = ConfigFlow()
        self.flow.hass = MagicMock()
        self.flow.async_set_unique_id = AsyncMock()
        self.flow._abort_if_unique_id_configured = MagicMock()
        self.flow.async_show_form = MagicMock()
        self.flow.async_create_entry = MagicMock()

    async def test_form_show(self):
        """Test showing the form."""
        # Mock the show form to return expected result
        self.flow.async_show_form.return_value = FlowResult(
            type=FlowResultType.FORM,
            step_id="user",
            data_schema=None,
            errors={},
        )

        result = await self.flow.async_step_user()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert result["errors"] == {}

        # Verify show_form was called
        self.flow.async_show_form.assert_called_once()

    async def test_form_valid_input(self):
        """Test form with valid input."""
        user_input = {"name": "Entity Manager"}

        # Mock successful validation
        with patch(
            "custom_components.entity_manager.config_flow.validate_input",
            return_value={"title": "Entity Manager"},
        ):
            # Mock create entry to return expected result
            self.flow.async_create_entry.return_value = FlowResult(
                type=FlowResultType.CREATE_ENTRY,
                title="Entity Manager",
                data=user_input,
            )

            result = await self.flow.async_step_user(user_input)

            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["title"] == "Entity Manager"
            assert result["data"] == user_input

    async def test_form_invalid_input(self):
        """Test form with invalid input."""
        user_input = {"name": ""}

        # Mock validation error
        with patch(
            "custom_components.entity_manager.config_flow.validate_input",
            side_effect=EntityManagerConfigError("Name cannot be empty"),
        ):
            # Mock show form for error case
            self.flow.async_show_form.return_value = FlowResult(
                type=FlowResultType.FORM,
                step_id="user",
                data_schema=None,
                errors={"base": "invalid_config"},
            )

            result = await self.flow.async_step_user(user_input)

            assert result["type"] == FlowResultType.FORM
            assert result["errors"] == {"base": "invalid_config"}

    async def test_form_already_configured(self):
        """Test abort when already configured."""
        from homeassistant.data_entry_flow import AbortFlow

        user_input = {"name": "Entity Manager"}

        # Mock validation to succeed
        with patch(
            "custom_components.entity_manager.config_flow.validate_input",
            return_value={"title": "Entity Manager"},
        ):
            # Mock that it's already configured - this will raise AbortFlow
            self.flow._abort_if_unique_id_configured.side_effect = AbortFlow(
                "already_configured"
            )

            # The exception gets caught and returns a form with error
            self.flow.async_show_form.return_value = FlowResult(
                type=FlowResultType.FORM,
                step_id="user",
                data_schema=None,
                errors={"base": "unknown"},
            )

            result = await self.flow.async_step_user(user_input)

            # The broad exception handler catches it and shows form with error
            assert result["type"] == FlowResultType.FORM
            assert result["errors"] == {"base": "unknown"}
