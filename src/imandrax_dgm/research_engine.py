"""Read-only, bounded external research and explicit OpenAI-compatible model client.

Neither component can write GitHub or invoke ChatGPT's native Deep Research.
The network-bearing proposer must run separately from the networkless evaluator.
"""
from __future__ import annotations
from dataclasses import dataclass
import ipaddress
import json
import re
from typing import Callable
from urllib.parse import urlencode, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler


class ResearchError(ValueError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ResearchError('Redirect refused: egress is fixed to explicitly trusted hosts')


def default_opener(req, timeout):
    return build_opener(NoRedirect()).open(req, timeout=timeout)


def _read_json(req, opener, max_bytes=512_000, timeout=12):
    try:
        with opener(req, timeout=timeout) as response:
            if getattr(response, 'status', 200) != 200:
                raise ResearchError('Remote service did not return HTTP 200')
            if 'application/json' not in response.headers.get('Content-Type', ''):
                raise ResearchError('Expected JSON content type')
            raw = response.read(max_bytes + 1)
    except ResearchError:
        raise
    except Exception as exc:
        raise ResearchError(f'Remote service unavailable: {type(exc).__name__}') from exc
    if len(raw) > max_bytes:
        raise ResearchError('Response exceeds byte budget')
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResearchError('Invalid remote JSON') from exc


@dataclass(frozen=True)
class LLMConfig:
    endpoint: str
    model: str
    api_key: str
    allowed_hosts: tuple[str, ...]

    def validate(self) -> bool:
        u = urlparse(self.endpoint)
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.fragment or u.query or u.port not in (None, 443):
            raise ResearchError('LLM endpoint must be a strict HTTPS URL')
        host = u.hostname.lower()
        try:
            ipaddress.ip_address(host)
            raise ResearchError('IP literal endpoints are forbidden')
        except ValueError as exc:
            if isinstance(exc, ResearchError):
                raise
        if host in ('localhost',) or host.endswith(('.local', '.internal')) or host not in self.allowed_hosts:
            raise ResearchError('LLM endpoint not in explicit host allowlist')
        if not self.model.strip() or not self.api_key.strip() or len(self.api_key) > 8192:
            raise ResearchError('Model and API key are required')
        return True


class LLMClient:
    def __init__(self, config: LLMConfig, opener: Callable = default_opener):
        config.validate()
        self.config = config
        self.opener = opener

    def complete_json(self, system: str, user: str) -> dict:
        if len(system) > 16000 or len(user) > 55000:
            raise ResearchError('Prompt budget exceeded')
        payload = {'model': self.config.model, 'temperature': 0.3,
                   'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}
        req = Request(self.config.endpoint, data=json.dumps(payload).encode(), method='POST', headers={
            'Authorization': f'Bearer {self.config.api_key}', 'Content-Type': 'application/json', 'Accept': 'application/json'})
        response = _read_json(req, self.opener, max_bytes=200_000, timeout=55)
        try:
            raw = response['choices'][0]['message']['content']
            if not isinstance(raw, str) or len(raw) > 160_000:
                raise ValueError('Invalid model message')
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                raise ValueError('Model did not return a JSON object')
            return obj
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ResearchError('Model output was not strict JSON proposal') from exc


class OpenAlexResearch:
    """Fixed-endpoint scholarly metadata retrieval, not an unrestricted web browser."""
    def __init__(self, opener: Callable = default_opener):
        self.opener = opener

    def search(self, query: str, per_page: int = 5) -> list[dict]:
        if not isinstance(query, str) or not 2 <= len(query) <= 180 or not 1 <= per_page <= 10:
            raise ResearchError('Research query exceeds budget')
        url = 'https://api.openalex.org/works?' + urlencode({'search': query, 'per-page': per_page,
                                                              'select': 'id,title,publication_year,doi'})
        req = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'ImandraX-DGM-Research/0.3 (public scholarly metadata)'})
        obj = _read_json(req, self.opener)
        if not isinstance(obj, dict) or not isinstance(obj.get('results'), list):
            raise ResearchError('Invalid OpenAlex response schema')
        hits = []
        for item in obj['results'][:per_page]:
            if not isinstance(item, dict):
                continue
            url = item.get('id', '')
            title = item.get('title', '')
            if not (isinstance(url, str) and re.fullmatch(r'https://openalex\.org/W[0-9]+', url) and
                    isinstance(title, str) and 1 <= len(title) <= 500):
                continue
            doi = item.get('doi')
            if not isinstance(doi, str) or not doi.startswith('https://doi.org/'):
                doi = None
            year = item.get('publication_year')
            hits.append({'title': title[:300], 'url': url, 'doi': doi,
                         'year': year if type(year) is int and 1900 <= year <= 2100 else None,
                         'provider': 'OpenAlex', 'retrieval_status': 'METADATA_ONLY'})
        return hits