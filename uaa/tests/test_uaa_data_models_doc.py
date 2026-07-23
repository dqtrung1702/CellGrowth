from pathlib import Path
import unittest


DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "uaa-data-models.html"


class UaaDataModelsDocTest(unittest.TestCase):
    def test_doc_exists_and_has_required_sections(self):
        self.assertTrue(DOC_PATH.exists(), f"Missing documentation file: {DOC_PATH}")

        content = DOC_PATH.read_text(encoding="utf-8")
        required_markers = [
            "UAA Data Models Atlas",
            "Business Overview",
            "Core Entity Relationship",
            "Overview Relationship View",
            "Approval Relationship View",
            "Identity Relationship View",
            "Schema Inventory",
            "Controller to Schema to Model Crosswalk",
            "AccessRequest",
            "ResponseEnvelope",
            "LoginRequest",
            "/getRoleList",
        ]

        for marker in required_markers:
            self.assertIn(marker, content, f"Expected marker not found: {marker}")


if __name__ == "__main__":
    unittest.main()
