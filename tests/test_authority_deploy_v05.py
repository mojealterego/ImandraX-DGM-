"""Independent authority must read secrets from isolated files, not agent env."""
from pathlib import Path
import os
import pytest
from imandrax_dgm.authority_cli import _load_token


def test_token_file_read_without_secret_in_environment(tmp_path,monkeypatch):
    token=tmp_path/'reviewer.token';token.write_text('x'*48+'\n')
    monkeypatch.setenv('RSI_AUTH_REVIEWER_TOKEN_FILE',str(token))
    monkeypatch.delenv('RSI_AUTH_REVIEWER_TOKEN',raising=False)
    assert _load_token('reviewer')=='x'*48


def test_conflicting_or_symlink_token_file_rejected(tmp_path,monkeypatch):
    token=tmp_path/'runner.token';token.write_text('x'*48)
    monkeypatch.setenv('RSI_AUTH_RUNNER_TOKEN_FILE',str(token))
    monkeypatch.setenv('RSI_AUTH_RUNNER_TOKEN','y'*48)
    with pytest.raises(ValueError):_load_token('runner')
    monkeypatch.delenv('RSI_AUTH_RUNNER_TOKEN')
    link=tmp_path/'alias.token';link.symlink_to(token)
    monkeypatch.setenv('RSI_AUTH_RUNNER_TOKEN_FILE',str(link))
    with pytest.raises(ValueError):_load_token('runner')


def test_authority_does_not_have_signer_or_git_write_permissions():
    root=Path(__file__).resolve().parents[1]
    dockerfile=(root/'deploy/authority/Dockerfile').read_text()
    compose=(root/'deploy/authority/compose.yaml').read_text()
    assert 'USER 10001' in dockerfile
    assert 'read_only: true' in compose
    assert 'cap_drop:' in compose
    assert 'no-new-privileges' in compose
    assert 'RSI_AUTH_REVIEWER_TOKEN_FILE' in compose
    assert 'RSI_AUTH_RUNNER_TOKEN_FILE' in compose
    assert 'RSI_AUTH_PROPOSER_TOKEN_FILE' in compose
    assert 'docker.sock' not in compose
    assert 'github_token' not in compose.lower()
