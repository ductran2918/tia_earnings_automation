"""Company-specific extractor registry and configuration."""
from typing import Dict, Optional, Callable
from pathlib import Path


# Import company-specific extraction functions
# These will be registered in the COMPANY_EXTRACTORS dict below
def _lazy_import_grab_extractor():
    """Lazy import to avoid circular dependencies."""
    from grab_extraction import extract_grab_data_with_llm
    return extract_grab_data_with_llm


def _lazy_import_sea_group_extractor():
    """Lazy import to avoid circular dependencies."""
    from sea_group_extraction import extract_sea_group_data_with_llm
    return extract_sea_group_data_with_llm


# Company extractor registry
# Maps company_slug -> configuration dict with extraction function, prompt, status
COMPANY_EXTRACTORS = {
    "grab-com": {
        "name": "Grab",
        "extraction_function": "extract_grab_data_with_llm",  # Lazy-loaded
        "button_label": "Extract Grab's metrics",
        "status": "implemented",  # "implemented" | "coming_soon" | "planned"
        "prompt_path": Path(__file__).parent.parent / "prompt" / "grab_com_extraction.md",
        "success_message": "Grab metrics extracted successfully. Review and push to database below.",
        "database_table": "grab_metrics",  # Supabase table name
        "has_database_push": True,  # Database push functionality enabled
    },
    "sea-group-garena": {
        "name": "Sea Group",
        "extraction_function": "extract_sea_group_data_with_llm",  # Lazy-loaded
        "button_label": "Extract Sea Group's metrics",
        "status": "implemented",  # "implemented" | "coming_soon" | "planned"
        "prompt_path": Path(__file__).parent.parent / "prompt" / "sea_group_extraction.md",
        "success_message": "Sea Group metrics extracted successfully. Review and push to database below.",
        "database_table": "seagroup_metrics",  # Supabase table name (no underscore to match Supabase)
        "has_database_push": True,  # Database push enabled
    },
    "alibaba-group": {
        "name": "Alibaba Group",
        "extraction_function": "extract_alibaba_data_with_llm",  # Lazy-loaded
        "button_label": "Extract Alibaba's metrics",
        "status": "implemented",  # "implemented" | "coming_soon" | "planned"
        "prompt_path": Path(__file__).parent.parent / "prompt" / "alibaba_group_extraction.md",
        "success_message": "Alibaba Group metrics extracted successfully. Review and push to database below.",
        "database_table": "alibaba_metrics",  # Supabase table name
        "has_database_push": True,  # Database push functionality enabled
    },
    "bukalapak": {
        "name": "Bukalapak",
        "extraction_function": None,
        "button_label": "Extract Bukalapak's metrics",
        "status": "coming_soon",
        "prompt_path": None,
        "success_message": None,
    },
    "vng-corp": {
        "name": "VNG (Vietnam)",
        "extraction_function": None,
        "button_label": "Extract VNG's metrics",
        "status": "coming_soon",
        "prompt_path": None,
        "success_message": None,
    },
}


def get_extractor_config(company_slug: str) -> Optional[Dict]:
    """Get extractor configuration for a company slug.

    Args:
        company_slug: Company slug (e.g., "grab-com")

    Returns:
        Configuration dict with keys: name, extraction_function, button_label,
        status, prompt_path, success_message. Returns None if slug not found.
    """
    return COMPANY_EXTRACTORS.get(company_slug)


def is_company_implemented(company_slug: str) -> bool:
    """Check if a company has a fully implemented extractor.

    Args:
        company_slug: Company slug (e.g., "grab-com")

    Returns:
        True if status is "implemented", False otherwise
    """
    config = get_extractor_config(company_slug)
    if not config:
        return False
    return config["status"] == "implemented"


def get_button_label_for_company(company_slug: str) -> str:
    """Get the extraction button label for a company.

    Args:
        company_slug: Company slug (e.g., "grab-com")

    Returns:
        Button label string (e.g., "Extract Grab's metrics")
        Falls back to "Extract Financial Data" if company not found
    """
    config = get_extractor_config(company_slug)
    if not config:
        return "Extract Financial Data"
    return config["button_label"]


def get_extraction_function(company_slug: str) -> Optional[Callable]:
    """Get the extraction function for a company.

    Args:
        company_slug: Company slug (e.g., "grab-com")

    Returns:
        Extraction function callable, or None if not implemented
    """
    config = get_extractor_config(company_slug)
    if not config or config["extraction_function"] is None:
        return None

    # Lazy load the function to avoid circular imports
    if config["extraction_function"] == "extract_grab_data_with_llm":
        from grab_extraction import extract_grab_data_with_llm
        return extract_grab_data_with_llm
    elif config["extraction_function"] == "extract_sea_group_data_with_llm":
        from sea_group_extraction import extract_sea_group_data_with_llm
        return extract_sea_group_data_with_llm
    elif config["extraction_function"] == "extract_alibaba_data_with_llm":
        from alibaba_extraction import extract_alibaba_data_with_llm
        return extract_alibaba_data_with_llm

    return None


def get_company_status(company_slug: str) -> str:
    """Get implementation status for a company.

    Args:
        company_slug: Company slug (e.g., "grab-com")

    Returns:
        Status string: "implemented" | "coming_soon" | "planned" | "unknown"
    """
    config = get_extractor_config(company_slug)
    if not config:
        return "unknown"
    return config["status"]
