#!/usr/bin/env python3
"""
Template loading and rendering utilities (v1)

Supports Markdown templates with YAML front matter and Jinja2 rendering.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, meta

TEMPLATES_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


@dataclass
class TemplateMetadata:
    name: str
    version: str = "1.0.0"
    type: str = "note"  # message | note | payload
    channels: Optional[list[str]] = None
    entity: Optional[str] = None
    required_vars: Optional[list[str]] = None
    defaults: Optional[Dict[str, Any]] = None


@dataclass
class LoadedTemplate:
    path: str
    rel_path: str
    meta: TemplateMetadata
    body: str


FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_front_matter(contents: str) -> tuple[Dict[str, Any], str]:
    match = FRONT_MATTER_RE.match(contents)
    if not match:
        return {}, contents
    yaml_text, body = match.groups()
    meta_dict = yaml.safe_load(yaml_text) or {}
    return meta_dict, body


def _env_with_root(root_dir: str) -> Environment:
    env = Environment(
        loader=FileSystemLoader(root_dir),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env


def discover_templates(root: str = TEMPLATES_ROOT) -> list[LoadedTemplate]:
    found: list[LoadedTemplate] = []
    if not os.path.isdir(root):
        return found

    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            if not filename.endswith((".md", ".markdown")):
                continue
            abs_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(abs_path, root)
            text = _read_file(abs_path)
            meta_dict, body = _parse_front_matter(text)
            meta_obj = TemplateMetadata(
                name=meta_dict.get("name") or os.path.splitext(filename)[0],
                version=str(meta_dict.get("version", "1.0.0")),
                type=str(meta_dict.get("type", "note")),
                channels=meta_dict.get("channels") or None,
                entity=meta_dict.get("entity") or None,
                required_vars=meta_dict.get("required_vars") or None,
                defaults=meta_dict.get("defaults") or None,
            )
            found.append(LoadedTemplate(path=abs_path, rel_path=rel_path, meta=meta_obj, body=body))
    return found


def load_template_by_name(name: str, root: str = TEMPLATES_ROOT) -> LoadedTemplate:
    candidates = discover_templates(root)
    for tmpl in candidates:
        if tmpl.meta.name == name or os.path.splitext(os.path.basename(tmpl.path))[0] == name:
            return tmpl
    raise FileNotFoundError(f"Template not found: {name}")


def validate_context(tmpl: LoadedTemplate, context: Dict[str, Any]) -> None:
    required = tmpl.meta.required_vars or []
    missing = [key for key in required if key not in context]
    if missing:
        raise ValueError(f"Missing required template variables: {', '.join(missing)}")


def render_template(tmpl: LoadedTemplate, context: Dict[str, Any]) -> str:
    # Merge defaults
    merged: Dict[str, Any] = {}
    if tmpl.meta.defaults:
        merged.update(tmpl.meta.defaults)
    merged.update(context)

    validate_context(tmpl, merged)

    # Render using a single-file environment rooted at the template's directory
    root_dir = os.path.dirname(tmpl.path)
    env = _env_with_root(root_dir)
    # Synthesize a template name for Jinja2 from the relative filename inside the directory
    filename = os.path.basename(tmpl.path)
    template = env.from_string(tmpl.body)
    return template.render(**merged)


