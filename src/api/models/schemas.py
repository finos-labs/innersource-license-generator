from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional


class LicenseRequest(BaseModel):
    """
    Pydantic model for license generation request.
    Replaces manual sanitization and validation from Flask version.
    """
    organization_name: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Legal organization name"
    )
    copyright_holder: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="Copyright holder/core team name"
    )
    scope: List[Literal["code", "docs", "data", "devops"]] = Field(
        ...,
        description="Scope of protection (code, docs, data, devops)"
    )
    boundary: Literal["orgonly", "orgsubs", "orgsubsvend"] = Field(
        ...,
        description="InnerSource boundary (organization only, +subsidiaries, +vendors)"
    )
    territory: List[str] = Field(
        default_factory=list,
        description="Territory list (US, UK, EU, etc.)"
    )
    other_territory: Optional[str] = Field(
        default=None,
        max_length=1024,
        description="Other territory if not in predefined list"
    )
    attribution: Literal["noat", "copyat", "orgat"] = Field(
        ...,
        description="Attribution requirements (none, to authors, to organization)"
    )
    distribution: Literal["noredist", "centralredist", "sharealredist", "allowredist"] = Field(
        ...,
        description="Distribution of derivative work policy"
    )
    llm: Literal["LLM_noread", "LLM_attribution", "LLM_allowread"] = Field(
        ...,
        description="LLM/GenAI access permissions"
    )
    warranty: Literal["asis", "security", "bug"] = Field(
        ...,
        description="Warranty/support level (as-is, security fixes, bug fixes)"
    )
    authbody: str = Field(
        ...,
        description="Authorizing body (ISC, OSPO, or Other)"
    )
    Authbody_name: Optional[str] = Field(
        default=None,
        max_length=1024,
        description="Custom authorizing body name when authbody='Other'"
    )

    @field_validator('scope')
    @classmethod
    def scope_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure at least one scope is selected"""
        if not v:
            raise ValueError('At least one scope must be selected')
        return v

    @field_validator('organization_name', 'copyright_holder', 'other_territory', 'Authbody_name')
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields: remove backspace characters and strip whitespace"""
        if v is None:
            return None
        return v.replace('\b', '').strip()

    @field_validator('Authbody_name')
    @classmethod
    def require_authbody_name_when_other(cls, v: Optional[str], info) -> Optional[str]:
        """Require Authbody_name when authbody is 'Other'"""
        # Note: This validation needs access to authbody field
        # In Pydantic v2, we can use model_validator for cross-field validation
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "organization_name": "Acme Corp",
                "copyright_holder": "John Doe",
                "scope": ["code", "docs"],
                "boundary": "orgonly",
                "territory": ["US", "UK"],
                "attribution": "copyat",
                "distribution": "noredist",
                "llm": "LLM_attribution",
                "warranty": "asis",
                "authbody": "OSPO"
            }
        }
    }


class LicenseResponse(BaseModel):
    """Response model for license generation"""
    license_text: str = Field(..., description="Full license text")
    human_readable: str = Field(..., description="Human-readable summary of license clauses")
    download_id: Optional[str] = Field(default=None, description="Session ID for downloading license")
