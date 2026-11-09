#!/usr/bin/env python3
"""Validate local case evidence declarations and render Markdown; no browser or API calls."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def text(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label}: non-empty text required")
    return value


def strings(value: object, label: str, nonempty: bool = False) -> list:
    require(isinstance(value, list), f"{label}: array required")
    require(not nonempty or bool(value), f"{label}: must not be empty")
    for item in value:
        text(item, label)
    return value


def obj(value: object, label: str) -> dict:
    require(isinstance(value, dict), f"{label}: object required")
    return value


def local_file(root: Path, value: object, label: str) -> Path:
    name = text(value, label)
    require(not Path(name).is_absolute(), f"{label}: use a relative evidence path")
    path = (root / name).resolve()
    require(path.is_relative_to(root), f"{label}: path escapes result directory")
    require(path.is_file() and path.stat().st_size > 0, f"{label}: missing or empty file: {name}")
    require(path.name not in {"result.json", "report.md"} and not path.is_relative_to(root / "cases"),
            f"{label}: generated output is not run evidence")
    return path


def validate(data: dict, root: Path) -> None:
    root = root.resolve()
    require(data.get("mode") in {"verified", "preview"}, "mode: verified or preview required")
    context = obj(data.get("project_context"), "project_context")
    case_project = obj(context.get("case_project"), "project_context.case_project")
    repositories = obj(context.get("automation_repositories"), "project_context.automation_repositories")
    context_states = {"resolved", "none", "unresolved", "inaccessible"}
    for label, entry in (("case_project", case_project), ("automation_repositories", repositories)):
        require(entry.get("status") in context_states, f"{label}: unsupported context status")
        text(entry.get("source"), f"{label}.source")
        text(entry.get("reason"), f"{label}.reason")
    if case_project["status"] == "resolved":
        text(case_project.get("location"), "case_project.location")
    elif case_project["status"] == "none":
        require(case_project.get("location") is None, "absent case project must not have a location")
    elif case_project.get("location") is not None:
        text(case_project["location"], "case_project.location")
    repo_entries = repositories.get("repositories")
    require(isinstance(repo_entries, list), "automation_repositories.repositories: array required")
    if repositories["status"] == "resolved":
        require(bool(repo_entries), "resolved automation context requires a repository")
    if repositories["status"] == "none":
        require(not repo_entries, "absent automation context must not list repositories")
    for repo in repo_entries:
        obj(repo, "repository")
        for key in ("location", "scope", "revision"):
            text(repo.get(key), f"repository.{key}")
    coverage = obj(data.get("coverage"), "coverage")
    cs = coverage.get("status")
    require(cs in {"complete", "not_applicable", "targeted", "unavailable"}, "coverage.status: unsupported")
    if cs in {"complete", "targeted"}:
        require(case_project["status"] == "resolved", "coverage search requires a resolved case project")
    if cs == "not_applicable":
        require(case_project["status"] == "none", "not_applicable requires confirmed absence of a case project")
    if case_project["status"] in {"unresolved", "inaccessible"}:
        require(cs == "unavailable", "unknown or inaccessible case project cannot claim completed coverage")
    text(coverage.get("scope"), "coverage.scope")
    text(coverage.get("reason"), "coverage.reason")
    queries = strings(coverage.get("queries"), "coverage.queries")
    if cs == "complete":
        require(len(set(queries)) >= 2, "complete coverage requires two distinct search queries")
    read_cases = coverage.get("read_cases")
    require(isinstance(read_cases, list), "coverage.read_cases: array required")
    read_refs = set()
    for item in read_cases:
        obj(item, "read case")
        read_refs.add(text(item.get("ref"), "read case.ref"))
        text(item.get("comparison"), "read case.comparison")
    not_done = strings(data.get("not_done"), "not_done")
    cases = data.get("cases")
    require(isinstance(cases, list), "cases: array required")
    require(bool(cases) or bool(not_done), "empty result must explain what was not done")
    ids = set()
    for case in cases:
        obj(case, "case")
        cid = text(case.get("id"), "case.id")
        require(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", cid)), "case.id: lowercase letters, digits and hyphens only")
        require(cid not in ids, f"duplicate case id: {cid}")
        ids.add(cid)
        for key in ("title", "reason"):
            text(case.get(key), f"{cid}.{key}")
        strings(case.get("sources"), f"{cid}.sources", nonempty=True)
        action, status = case.get("action"), case.get("status")
        require(action in {"create", "update", "unchanged", "none"}, f"{cid}: unsupported action")
        changed = action in {"create", "update"}
        if action in {"update", "unchanged"}:
            require(case_project["status"] == "resolved", f"{cid}: existing case requires a resolved project")
            ref = text(case.get("existing_ref"), f"{cid}.existing_ref")
            require(ref in read_refs, f"{cid}: existing case must be fully read and compared")
        if not changed:
            require(status == "unchanged", f"{cid}: no change must use unchanged status")
            require("external" not in case, f"{cid}: unchanged decision must not claim an external write")
            continue
        require(status in {"draft", "blocked", "preview"}, f"{cid}: unsupported status")
        require(status != "preview" or data["mode"] == "preview", f"{cid}: preview requires explicit preview mode")
        require(data["mode"] != "preview" or status != "draft", f"{cid}: early preview must not claim verified draft")
        if status == "draft":
            require(cs != "unavailable", f"{cid}: coverage is unavailable")
            require(cs != "targeted" or action == "update", f"{cid}: targeted search cannot justify new case")
        strings(case.get("preconditions"), f"{cid}.preconditions")
        strings(case.get("variants"), f"{cid}.variants")
        steps = case.get("steps")
        require(isinstance(steps, list) and bool(steps), f"{cid}: non-empty steps required")
        for step in steps:
            obj(step, f"{cid}.step")
            text(step.get("action"), f"{cid}.step.action")
            text(step.get("expected"), f"{cid}.step.expected")
        verification = obj(case.get("verification"), f"{cid}.verification")
        basis = verification.get("basis")
        require(basis in {"new_run", "existing_report", "mixed", "none"}, f"{cid}: unsupported verification basis")
        require(type(verification.get("new_run")) is bool, f"{cid}: new_run must be boolean")
        require(verification["new_run"] == (basis in {"new_run", "mixed"}), f"{cid}: new_run contradicts basis")
        result = verification.get("result")
        require(result in {"passed", "failed", "partial", "not_run"}, f"{cid}: unsupported run result")
        require((basis == "none") == (result == "not_run"), f"{cid}: verification basis contradicts run result")
        for key in ("environment", "version", "checked_at", "scope"):
            text(verification.get(key), f"{cid}.verification.{key}")
        covered = verification.get("covered_steps")
        require(isinstance(covered, list) and all(type(n) is int and 1 <= n <= len(steps) for n in covered),
                f"{cid}: covered_steps must reference existing step numbers")
        require(len(covered) == len(set(covered)), f"{cid}: duplicate covered_steps")
        artifacts = strings(verification.get("artifacts"), f"{cid}.verification.artifacts")
        artifact_paths = [local_file(root, p, f"{cid}.artifact") for p in artifacts]
        limitations = strings(verification.get("limitations"), f"{cid}.verification.limitations")
        if status == "draft":
            require(result == "passed" and basis != "none", f"{cid}: draft requires successful actual verification")
            require(set(covered) == set(range(1, len(steps) + 1)), f"{cid}: not all steps are verified")
            require(bool(artifact_paths) and not limitations, f"{cid}: draft requires evidence without unresolved limitations")
            require(any(p.suffix.lower() in {".md", ".txt", ".json", ".jsonl", ".html", ".zip"} for p in artifact_paths),
                    f"{cid}: screenshots alone are not an execution report")
        if status == "blocked":
            require(bool(limitations), f"{cid}: blocked case must explain the limitation")
        if "estimate" in case or status == "draft":
            estimate = obj(case.get("estimate"), f"{cid}.estimate")
            require(type(estimate.get("seconds")) is int and estimate["seconds"] > 0, f"{cid}: positive estimate in seconds required")
            text(estimate.get("basis"), f"{cid}.estimate.basis")
        media = obj(case.get("media"), f"{cid}.media")
        require(type(media.get("required")) is bool, f"{cid}: media.required must be boolean")
        text(media.get("reason"), f"{cid}.media.reason")
        items = media.get("items")
        require(isinstance(items, list), f"{cid}: media.items must be an array")
        if status == "draft" and media["required"]:
            require(bool(items), f"{cid}: required media are missing")
        for item in items:
            obj(item, f"{cid}.media.item")
            local_file(root, item.get("path"), f"{cid}.media.path")
            require(item.get("role") in {"product", "design", "attachment"}, f"{cid}: unsupported image role")
            text(item.get("caption"), f"{cid}.media.caption")
            require(type(item.get("step")) is int and 0 <= item["step"] <= len(steps), f"{cid}: invalid media step")
            require(item.get("viewed") is True, f"{cid}: media must be visually inspected")
        if status == "draft" or "automation" in case:
            auto = obj(case.get("automation"), f"{cid}.automation")
            strings(auto.get("checked"), f"{cid}.automation.checked", nonempty=True)
            gaps = strings(auto.get("gaps"), f"{cid}.automation.gaps")
            require(auto.get("action") in {"add", "update", "covered", "not_needed", "blocked"}, f"{cid}: invalid automation action")
            if repositories["status"] != "resolved":
                require(auto["action"] == "blocked", f"{cid}: automation conclusion requires a resolved repository")
            for key in ("target", "reason"):
                text(auto.get(key), f"{cid}.automation.{key}")
            found = auto.get("found")
            require(isinstance(found, list), f"{cid}: automation.found must be an array")
            for item in found:
                obj(item, f"{cid}.automation.found")
                text(item.get("ref"), f"{cid}.automation.ref")
                text(item.get("covers"), f"{cid}.automation.covers")
            require(auto["action"] not in {"add", "update"} or bool(gaps), f"{cid}: automation change needs a concrete gap")
            require(auto["action"] != "covered" or bool(found), f"{cid}: covered requires inspected tests")
        if "external" in case:
            external = obj(case["external"], f"{cid}.external")
            for key in ("system", "case_ref"):
                text(external.get(key), f"{cid}.external.{key}")
            require(external.get("state") in {"verified", "unconfirmed"}, f"{cid}: invalid external state")
            paths = strings(external.get("readback"), f"{cid}.external.readback")
            for path in paths:
                local_file(root, path, f"{cid}.external.readback")
            checked = strings(external.get("checked"), f"{cid}.external.checked")
            if external["state"] == "verified":
                require(bool(paths), f"{cid}: external success requires saved readback")
                require({"draft", "content", "estimate", "source_links", "media"}.issubset(checked),
                        f"{cid}: external readback checks are incomplete")
            else:
                require(status == "blocked", f"{cid}: unconfirmed external write must remain blocked")


def bullets(items: list) -> list[str]:
    return [f"- {item}" for item in items] or ["- Не требуются / отсутствуют в указанной области."]


def artifact_link(path: str) -> str:
    return quote("../" + path, safe="/")


def render_case(case: dict) -> str:
    lines = [f"# {case['title']}", "", f"**Действие:** {case['action']} · **Статус:** {case['status']}",
             "", case["reason"], "", "## Источники", "", *bullets(case["sources"])]
    if case.get("existing_ref"):
        lines += ["", f"**Существующий кейс:** {case['existing_ref']}"]
    if case["action"] in {"unchanged", "none"}:
        return "\n".join(lines) + "\n"
    lines += ["", "## Предусловия", "", *bullets(case["preconditions"])]
    if case["variants"]:
        lines += ["", "## Проверяемые варианты", "", *bullets(case["variants"])]
    media = case["media"]
    for item in media["items"]:
        if item["step"] == 0:
            lines += ["", f"![{cell(item['caption'])}]({artifact_link(item['path'])})", f"Источник: {item['role']}."]
    lines += ["", "## Шаги", ""]
    for number, step in enumerate(case["steps"], 1):
        lines += [f"{number}. {step['action']}", f"   Ожидается: {step['expected']}"]
        for item in media["items"]:
            if item["step"] == number:
                lines += [f"\n   ![{cell(item['caption'])}]({artifact_link(item['path'])})", f"   Источник: {item['role']}."]
    if "estimate" in case:
        lines += ["", f"**Оценка полного прохода:** {case['estimate']['seconds']} с. {case['estimate']['basis']}"]
    v = case["verification"]
    lines += ["", "## Подтверждение прохождения", "",
              f"Основание: {v['basis']}. Результат: {v['result']}. Новый прогон: {'да' if v['new_run'] else 'нет'}.",
              f"Среда: {v['environment']}. Версия: {v['version']}. Проверка: {v['checked_at']}.",
              "", f"Проверенная область: {v['scope']}",
              f"Подтверждённые шаги: {', '.join(map(str, v['covered_steps'])) or 'нет'}."]
    for path in v["artifacts"]:
        lines += [f"- [Артефакт]({artifact_link(path)})"]
    lines += ["", f"**Медиа:** {media['reason']}"]
    if v["limitations"]:
        lines += ["", "## Ограничения", "", *bullets(v["limitations"])]
    if "automation" in case:
        a = case["automation"]
        lines += ["", "## Автопокрытие", "", "Просмотрено:", *bullets(a["checked"]), "", "Найдено:",
                  *bullets([f"{f['ref']}: {f['covers']}" for f in a["found"]]), "", "Пробелы:", *bullets(a["gaps"]),
                  "", f"Рекомендация: {a['action']} / {a['target']}. {a['reason']}"]
    if "external" in case:
        e = case["external"]
        lines += ["", "## Внешняя запись", "", f"{e['system']}: {e['case_ref']}. Состояние: {e['state']}."]
        lines += [f"- [Readback]({artifact_link(p)})" for p in e["readback"]]
    return "\n".join(lines) + "\n"


def cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def render_report(data: dict) -> str:
    context = data["project_context"]
    project = context["case_project"]
    repos = context["automation_repositories"]
    lines = ["# Результат", "", f"Режим: {data['mode']}. Результат сохранён локально.", "",
             "## Контекст проекта", "",
             f"**База кейсов:** {project.get('location') or 'не указана'}; {project['status']}.",
             f"Источник: {project['source']}. {project['reason']}", "",
             f"**Репозитории автоматизации:** {repos['status']}. {repos['reason']}",
             f"Источник: {repos['source']}."]
    for repo in repos["repositories"]:
        lines += [f"- {repo['location']} — область: {repo['scope']}; версия: {repo['revision']}."]
    lines += ["", "## Решения", "",
             "| Сценарий | Решение | Статус | Основание прохождения |", "|---|---|---|---|"]
    for c in data["cases"]:
        basis = c.get("verification", {}).get("basis", "Не требовалось")
        lines += [f"| [{cell(c['title'])}](cases/{c['id']}.md) | {c['action']} | {c['status']} | {basis} |"]
    coverage = data["coverage"]
    lines += ["", f"**Поиск покрытия:** {coverage['status']}. {coverage['scope']}", coverage["reason"]]
    for c in data["cases"]:
        if c["action"] not in {"create", "update"}:
            continue
        v = c["verification"]
        lines += ["", f"**{c['title']}:** новый прогон — {'да' if v['new_run'] else 'нет'}; {v['result']}. {v['scope']}"]
        lines += bullets(v["limitations"]) if v["limitations"] else []
        if "automation" in c:
            a = c["automation"]
            lines += [f"Автопокрытие: {a['action']} / {a['target']}. {a['reason']}"]
        if "external" in c:
            e = c["external"]
            lines += [f"Внешняя запись: {e['state']} — {e['system']}, {e['case_ref']}."]
    if data["not_done"]:
        lines += ["", "## Требуется внимание", "", *bullets(data["not_done"])]
    lines += ["", "Проверка структуры и файлов не заменяет проверку требований и фактическое прохождение."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        source = args.input.resolve()
        data = obj(json.loads(source.read_text(encoding="utf-8")), "result")
        validate(data, source.parent)
        rendered = [(c["id"], render_case(c)) for c in data["cases"]]
        report = render_report(data)
        target = source.parent / "cases"
        require(not target.is_symlink(), "cases directory must not be a symlink")
        target.mkdir(exist_ok=True)
        for cid, content in rendered:
            destination = target / f"{cid}.md"
            require(not destination.is_symlink(), "case destination must not be a symlink")
            destination.write_text(content, encoding="utf-8")
        destination = source.parent / "report.md"
        require(not destination.is_symlink(), "report destination must not be a symlink")
        destination.write_text(report, encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, ContractError) as error:
        print(f"finalize-cases: {error}")
        return 2
    print(f"Validated {len(data['cases'])} decision(s). Report: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
