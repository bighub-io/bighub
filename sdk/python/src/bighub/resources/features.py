from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class FeaturesAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def compute(
        self,
        *,
        case_id: str,
        org_id: str,
        case_data: JSONDict,
        precedent_data: Optional[JSONDict] = None,
        advisory_data: Optional[JSONDict] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "org_id": org_id,
            "case_data": case_data,
        }
        if precedent_data is not None:
            body["precedent_data"] = precedent_data
        if advisory_data is not None:
            body["advisory_data"] = advisory_data
        return self._transport.request(
            method="POST", path="/features/compute", json_body=body
        )

    def snapshot(
        self,
        *,
        case_id: str,
        tag: Optional[str] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"case_id": case_id}
        if tag is not None:
            body["tag"] = tag
        return self._transport.request(
            method="POST", path="/features/snapshot", json_body=body
        )

    def get_snapshot(self, snapshot_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/features/snapshot/{snapshot_id}"
        )

    def list_snapshots(
        self,
        *,
        tag: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if tag is not None:
            params["tag"] = tag
        if case_id is not None:
            params["case_id"] = case_id
        return self._transport.request(
            method="GET", path="/features/snapshots", params=params
        )

    def explain(
        self,
        case_id: str,
        *,
        feature_key: Optional[str] = None,
    ) -> JSONDict:
        if feature_key is not None:
            return self._transport.request(
                method="GET",
                path=f"/features/explain/{case_id}/{feature_key}",
            )
        return self._transport.request(
            method="GET", path=f"/features/explain/{case_id}"
        )

    def export(self, case_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/features/export/{case_id}"
        )

    def schema(self) -> JSONDict:
        return self._transport.request(method="GET", path="/features/schema")

    def compute_batch(
        self,
        *,
        cases: List[JSONDict],
    ) -> JSONDict:
        """Compute feature vectors for multiple cases (max 500)."""
        return self._transport.request(
            method="POST", path="/features/compute/batch", json_body={"cases": cases}
        )

    def compare(
        self,
        *,
        snapshot_id_a: Optional[str] = None,
        snapshot_id_b: Optional[str] = None,
        case_id_a: Optional[str] = None,
        case_id_b: Optional[str] = None,
        changed_only: bool = True,
    ) -> JSONDict:
        """Compare two feature snapshots or cached vectors. Returns changed features."""
        body: Dict[str, Any] = {"changed_only": changed_only}
        if snapshot_id_a is not None:
            body["snapshot_id_a"] = snapshot_id_a
        if snapshot_id_b is not None:
            body["snapshot_id_b"] = snapshot_id_b
        if case_id_a is not None:
            body["case_id_a"] = case_id_a
        if case_id_b is not None:
            body["case_id_b"] = case_id_b
        return self._transport.request(
            method="POST", path="/features/compare", json_body=body
        )

    def export_batch(
        self,
        *,
        case_ids: List[str],
    ) -> JSONDict:
        """Export flat feature dicts for multiple cases (max 500)."""
        return self._transport.request(
            method="POST", path="/features/export/batch", json_body={"case_ids": case_ids}
        )

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/features/stats")


class AsyncFeaturesAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def compute(
        self,
        *,
        case_id: str,
        org_id: str,
        case_data: JSONDict,
        precedent_data: Optional[JSONDict] = None,
        advisory_data: Optional[JSONDict] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "org_id": org_id,
            "case_data": case_data,
        }
        if precedent_data is not None:
            body["precedent_data"] = precedent_data
        if advisory_data is not None:
            body["advisory_data"] = advisory_data
        return await self._transport.request(
            method="POST", path="/features/compute", json_body=body
        )

    async def snapshot(
        self,
        *,
        case_id: str,
        tag: Optional[str] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"case_id": case_id}
        if tag is not None:
            body["tag"] = tag
        return await self._transport.request(
            method="POST", path="/features/snapshot", json_body=body
        )

    async def get_snapshot(self, snapshot_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/features/snapshot/{snapshot_id}"
        )

    async def list_snapshots(
        self,
        *,
        tag: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if tag is not None:
            params["tag"] = tag
        if case_id is not None:
            params["case_id"] = case_id
        return await self._transport.request(
            method="GET", path="/features/snapshots", params=params
        )

    async def explain(
        self,
        case_id: str,
        *,
        feature_key: Optional[str] = None,
    ) -> JSONDict:
        if feature_key is not None:
            return await self._transport.request(
                method="GET",
                path=f"/features/explain/{case_id}/{feature_key}",
            )
        return await self._transport.request(
            method="GET", path=f"/features/explain/{case_id}"
        )

    async def export(self, case_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/features/export/{case_id}"
        )

    async def schema(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/features/schema"
        )

    async def compute_batch(
        self,
        *,
        cases: List[JSONDict],
    ) -> JSONDict:
        """Compute feature vectors for multiple cases (max 500)."""
        return await self._transport.request(
            method="POST", path="/features/compute/batch", json_body={"cases": cases}
        )

    async def compare(
        self,
        *,
        snapshot_id_a: Optional[str] = None,
        snapshot_id_b: Optional[str] = None,
        case_id_a: Optional[str] = None,
        case_id_b: Optional[str] = None,
        changed_only: bool = True,
    ) -> JSONDict:
        """Compare two feature snapshots or cached vectors. Returns changed features."""
        body: Dict[str, Any] = {"changed_only": changed_only}
        if snapshot_id_a is not None:
            body["snapshot_id_a"] = snapshot_id_a
        if snapshot_id_b is not None:
            body["snapshot_id_b"] = snapshot_id_b
        if case_id_a is not None:
            body["case_id_a"] = case_id_a
        if case_id_b is not None:
            body["case_id_b"] = case_id_b
        return await self._transport.request(
            method="POST", path="/features/compare", json_body=body
        )

    async def export_batch(
        self,
        *,
        case_ids: List[str],
    ) -> JSONDict:
        """Export flat feature dicts for multiple cases (max 500)."""
        return await self._transport.request(
            method="POST", path="/features/export/batch", json_body={"case_ids": case_ids}
        )

    async def stats(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/features/stats"
        )
