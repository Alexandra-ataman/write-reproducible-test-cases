"""Contract checks on synthetic declarations, not proof of a real browser run."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "finalize_cases.py"
SPEC = importlib.util.spec_from_file_location("finalize_cases", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.addCleanup(self.temp.cleanup)
        (self.root / "evidence").mkdir()
        (self.root / "evidence" / "run.md").write_text(
            "Synthetic contract fixture. No real application or browser was tested.\n", encoding="utf-8")
        self.data = {
            "mode": "verified",
            "project_context": {
                "case_project": {"status": "resolved", "location": "Synthetic TMS project", "source": "Synthetic user answer", "reason": "Project selected for fixture"},
                "automation_repositories": {"status": "inaccessible", "repositories": [], "source": "Synthetic user answer", "reason": "Code access not available in fixture"}
            },
            "coverage": {"status": "complete", "scope": "Synthetic case corpus", "queries": ["save preference", "setting persists"],
                         "read_cases": [], "reason": "Synthetic search completed without matching cases"},
            "cases": [{
                "id": "save-setting", "title": "Synthetic save setting", "action": "create", "status": "draft",
                "reason": "Independent path in a synthetic contract fixture", "sources": ["Synthetic requirements"],
                "preconditions": ["Synthetic initial state"], "variants": [],
                "steps": [{"action": "Save setting", "expected": "Setting persists"}],
                "estimate": {"seconds": 60, "basis": "Synthetic estimate"},
                "verification": {"basis": "new_run", "new_run": True, "result": "passed",
                                 "environment": "Synthetic fixture, not a real browser", "version": "fixture-v1",
                                 "checked_at": "Fixture only", "scope": "Synthetic declared step",
                                 "covered_steps": [1], "artifacts": ["evidence/run.md"], "limitations": []},
                "media": {"required": False, "reason": "Not needed for synthetic fixture", "items": []},
                "automation": {"checked": ["Code unavailable in fixture"], "found": [], "gaps": [],
                               "action": "blocked", "target": "Project code", "reason": "Access needed"}
            }], "not_done": []}

    def case(self):
        return self.data["cases"][0]

    def reject(self):
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate(self.data, self.root)

    def test_accepts_complete_local_contract(self):
        MODULE.validate(self.data, self.root)

    def test_cli_renders_readable_artifact_links(self):
        source = self.root / "result.json"
        source.write_text(json.dumps(self.data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        report = (self.root / "report.md").read_text()
        case = (self.root / "cases" / "save-setting.md").read_text()
        self.assertIn("cases/save-setting.md", report)
        self.assertIn("../evidence/run.md", case)
        self.assertIn("Setting persists", case)

    def test_early_preview_remains_unverified(self):
        self.data["mode"] = "preview"
        self.case()["status"] = "preview"
        v = self.case()["verification"]
        v.update(basis="none", new_run=False, result="not_run", covered_steps=[], artifacts=[])
        MODULE.validate(self.data, self.root)
        self.assertIn("not_run", MODULE.render_report(self.data))

    def test_rejects_verified_draft_in_preview_mode(self):
        self.data["mode"] = "preview"
        self.reject()

    def test_rejects_draft_without_run(self):
        self.case()["verification"].update(basis="none", new_run=False, result="not_run")
        self.reject()

    def test_old_report_does_not_claim_new_run(self):
        self.case()["verification"].update(basis="existing_report", new_run=False)
        MODULE.validate(self.data, self.root)
        self.assertIn("новый прогон — нет", MODULE.render_report(self.data))

    def test_rejects_contradictory_report_provenance(self):
        self.case()["verification"].update(basis="existing_report", new_run=True)
        self.reject()

    def test_rejects_uncovered_step(self):
        self.case()["steps"].append({"action": "Reopen", "expected": "Saved value visible"})
        self.reject()

    def test_rejects_partial_run_as_ready(self):
        self.case()["verification"]["result"] = "partial"
        self.reject()

    def test_rejects_target_limitations_as_ready(self):
        self.case()["verification"]["limitations"] = ["Target webview navigation not checked"]
        self.reject()

    def test_allows_blocked_result_without_fake_evidence(self):
        self.case()["status"] = "blocked"
        self.case()["verification"].update(basis="none", new_run=False, result="not_run", artifacts=[],
                                           covered_steps=[], limitations=["Need accessible build"])
        self.data["coverage"]["status"] = "unavailable"
        MODULE.validate(self.data, self.root)

    def test_rejects_missing_evidence(self):
        (self.root / "evidence" / "run.md").unlink()
        self.reject()

    def test_rejects_screenshots_as_only_run_evidence(self):
        (self.root / "evidence" / "screenshot.png").write_bytes(b"Synthetic placeholder")
        self.case()["verification"]["artifacts"] = ["evidence/screenshot.png"]
        self.reject()

    def test_rejects_incomplete_search_as_ready(self):
        self.data["coverage"]["status"] = "unavailable"
        self.reject()

    def test_rejects_single_search_as_complete(self):
        self.data["coverage"]["queries"] = ["save preference"]
        self.reject()

    def test_rejects_targeted_search_for_new_case(self):
        self.data["coverage"]["status"] = "targeted"
        self.reject()

    def test_update_requires_read_original(self):
        self.case().update(action="update", existing_ref="cases/original.md")
        self.reject()
        self.data["coverage"]["read_cases"] = [{"ref": "cases/original.md", "comparison": "Same path; extend expected result"}]
        MODULE.validate(self.data, self.root)

    def test_rejects_missing_required_media(self):
        self.case()["media"]["required"] = True
        self.reject()

    def test_rejects_uninspected_media(self):
        (self.root / "evidence" / "screen.png").write_bytes(b"Synthetic placeholder")
        self.case()["media"]["items"] = [{"path": "evidence/screen.png", "role": "product", "caption": "Fixture", "step": 1, "viewed": False}]
        self.reject()

    def test_rejects_claimed_automation_without_found_test(self):
        self.case()["automation"]["action"] = "covered"
        self.reject()

    def test_rejects_automation_change_without_gap(self):
        self.case()["automation"]["action"] = "add"
        self.reject()

    def test_rejects_missing_automation_analysis(self):
        del self.case()["automation"]
        self.reject()

    def test_rejects_external_success_without_readback(self):
        self.case()["external"] = {"system": "Example TMS", "case_ref": "fixture-id", "state": "verified",
                                   "readback": [], "checked": ["draft", "content", "estimate", "source_links", "media"]}
        self.reject()

    def test_rejects_unconfirmed_external_write_as_ready(self):
        self.case()["external"] = {"system": "Example TMS", "case_ref": "fixture-id", "state": "unconfirmed", "readback": [], "checked": []}
        self.reject()

    def test_rejects_path_escape(self):
        self.case()["verification"]["artifacts"] = ["../outside.md"]
        self.reject()

    def test_rejects_duplicate_case_ids(self):
        self.data["cases"].append(copy.deepcopy(self.case()))
        self.reject()

    def test_rejects_generated_report_as_evidence(self):
        (self.root / "report.md").write_text("Old generated report")
        self.case()["verification"]["artifacts"] = ["report.md"]
        self.reject()

    def test_invalid_cli_does_not_render_new_success(self):
        self.case()["verification"]["result"] = "failed"
        source = self.root / "result.json"
        source.write_text(json.dumps(self.data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "report.md").exists())

    def test_artifact_names_with_spaces_remain_clickable(self):
        (self.root / "evidence" / "run notes.md").write_text("Synthetic trace")
        self.case()["verification"]["artifacts"] = ["evidence/run notes.md"]
        MODULE.validate(self.data, self.root)
        self.assertIn("../evidence/run%20notes.md", MODULE.render_case(self.case()))

    def test_requires_explicit_project_context(self):
        del self.data["project_context"]
        self.reject()

    def test_unknown_case_project_cannot_claim_completed_search(self):
        self.data["project_context"]["case_project"].update(status="unresolved", location=None)
        self.reject()

    def test_no_case_project_requires_confirmed_absence(self):
        self.data["coverage"]["status"] = "not_applicable"
        self.reject()
        self.data["project_context"]["case_project"].update(status="none", location=None, reason="User confirmed no case corpus exists")
        MODULE.validate(self.data, self.root)

    def test_resolved_case_project_requires_location(self):
        self.data["project_context"]["case_project"]["location"] = None
        self.reject()

    def test_unknown_automation_source_cannot_claim_no_tests(self):
        self.case()["automation"].update(action="add", gaps=["Path not protected by inspected tests"])
        self.reject()

    def test_resolved_automation_requires_repository_and_scope(self):
        context = self.data["project_context"]["automation_repositories"]
        context.update(status="resolved", repositories=[])
        self.reject()
        context["repositories"] = [{"location": "Synthetic repository", "scope": "tests/settings", "revision": "fixture-v1"}]
        self.case()["automation"].update(action="add", gaps=["Inspected tests do not protect the save path"])
        MODULE.validate(self.data, self.root)
        del context["repositories"][0]["scope"]
        self.reject()

    def test_supports_separate_product_and_e2e_repositories(self):
        context = self.data["project_context"]["automation_repositories"]
        context.update(status="resolved", repositories=[
            {"location": "Synthetic product repo", "scope": "web/settings", "revision": "fixture-v1"},
            {"location": "Synthetic E2E repo", "scope": "specs/settings", "revision": "fixture-v2"}])
        MODULE.validate(self.data, self.root)
        report = MODULE.render_report(self.data)
        self.assertIn("Synthetic product repo", report)
        self.assertIn("Synthetic E2E repo", report)

    def test_records_source_of_user_project_choice(self):
        report = MODULE.render_report(self.data)
        self.assertIn("Synthetic user answer", report)
        self.assertIn("Synthetic TMS project", report)

    def test_unknown_project_allows_only_blocked_proposal(self):
        self.data["project_context"]["case_project"].update(status="unresolved", location=None)
        self.data["coverage"]["status"] = "unavailable"
        self.case()["status"] = "blocked"
        self.case()["verification"]["limitations"] = ["Need user to identify case corpus"]
        MODULE.validate(self.data, self.root)


if __name__ == "__main__":
    unittest.main()
